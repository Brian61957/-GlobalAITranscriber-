"""
browser_process.py

Runs Playwright using the ASYNC API inside a dedicated thread that
owns its own asyncio event loop. This is the correct approach for
Windows Python 3.9 + Streamlit:

- We use async_playwright (not sync_playwright) -- no event-loop conflict
- The worker thread creates its own ProactorEventLoop via asyncio.run()
- Streamlit's main thread is completely isolated from Playwright's loop
"""

import queue
import threading
import time
import traceback
import asyncio
import sys


# --------------------------------------------------
# Messages
# --------------------------------------------------

class OpenAndUnderstandMsg:
    def __init__(self, url, model_choice, language_choice):
        self.url = url
        self.model_choice = model_choice
        self.language_choice = language_choice

class TranscribeMsg:
    pass

class FillTranscriptMsg:
    def __init__(self, text):
        self.text = text

class NextTaskMsg:
    pass

class SubmitMsg:
    def __init__(self, text):
        self.text = text

class CloseMsg:
    pass

class EventMsg:
    def __init__(self, step, status, detail=""):
        self.step = step
        self.status = status
        self.detail = detail

class ResultMsg:
    def __init__(self, value):
        self.value = value

class ErrorMsg:
    def __init__(self, message):
        self.message = message


# --------------------------------------------------
# Async browser manager (wraps all Playwright calls)
# --------------------------------------------------

class AsyncBrowserManager:
    """Async version of BrowserManager using async_playwright."""

    def __init__(self, domain="default"):
        self.domain = domain
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.media_requests = []
        self.latest_media_url = None
        self.media_extensions = (".wav", ".mp3", ".ogg", ".m4a", ".aac", ".flac", ".opus")

        from browser.session_storage import SessionStorage
        from browser.auth_manager import AuthManager
        self.session_storage = SessionStorage(domain)
        self.auth = AuthManager(self.session_storage)

    def _handle_request(self, request):
        try:
            url = request.url
            if url.lower().endswith(self.media_extensions):
                self.media_requests.append(url)
                self.latest_media_url = url
                from utils.logger import logger
                logger.info(f"MEDIA DETECTED: {url}")
        except Exception:
            pass

    async def start(self):
        from playwright.async_api import async_playwright
        from utils.logger import logger

        if self.page is not None:
            logger.info("Browser already running.")
            return

        logger.info("Starting browser...")
        logger.info("Step 1/4: launching Playwright driver...")
        self.playwright = await async_playwright().start()
        logger.info("Step 1/4 done: Playwright driver launched.")

        logger.info("Step 2/4: launching Chromium...")
        self.browser = await self.playwright.chromium.launch(headless=True)
        logger.info("Step 2/4 done: Chromium launched.")

        logger.info("Step 3/4: creating browser context...")
        if self.auth.has_saved_session():
            logger.info("Loading saved browser session...")
            self.context = await self.browser.new_context(
                storage_state=self.auth.session_path()
            )
        else:
            logger.info("No saved session found.")
            self.context = await self.browser.new_context()
        logger.info("Step 3/4 done: browser context created.")

        logger.info("Step 4/4: opening a new page...")
        self.page = await self.context.new_page()
        self.page.on("request", self._handle_request)
        logger.info("Step 4/4 done: page opened.")
        logger.info("Network monitor started.")

    async def fresh_context(self):
        from utils.logger import logger
        logger.info("Creating a fresh browser context...")
        try:
            if self.page:
                await self.page.close()
        except Exception:
            pass
        try:
            if self.context:
                await self.context.close()
        except Exception:
            pass
        self.page = None
        self.context = None
        self.media_requests.clear()
        self.latest_media_url = None
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        self.page.on("request", self._handle_request)
        logger.info("Fresh context ready.")

    async def open_project(self, url):
        from utils.logger import logger
        from utils.url_utils import normalize_url
        logger.info("Opening project...")
        self.clear_media_requests()
        url = normalize_url(url)
        try:
            await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            if "Timeout" in type(e).__name__:
                logger.warning("Navigation timed out.")
            else:
                raise RuntimeError(f"Couldn't open '{url}'. Details: {e}")
        await self.page.wait_for_timeout(2000)
        for selector in ["textarea", "button", "audio", "body"]:
            try:
                await self.page.wait_for_selector(selector, timeout=5000)
                logger.info(f"Page ready ({selector})")
                break
            except Exception:
                pass
        logger.info("Project opened successfully.")

    async def save_session(self):
        from utils.logger import logger
        if self.context is None:
            return
        logger.info("Saving browser session...")
        await self.context.storage_state(path=self.auth.session_path())
        logger.info("Session saved successfully.")

    async def close(self):
        from utils.logger import logger
        logger.info("Closing browser...")
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception:
            pass
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def clear_media_requests(self):
        self.media_requests.clear()
        self.latest_media_url = None

    def get_page(self):
        return self.page

    def is_login_page(self):
        try:
            url = self.page.url.lower()
            return any(k in url for k in ("login", "signin", "sign-in", "auth"))
        except Exception:
            return False

    async def attempt_auto_login(self, email, password):
        """
        Best-effort automated login using stored credentials, so the app
        can work on headless cloud hosting where nobody can see the
        browser window to log in manually.

        This is heuristic (there's no fixed Intron login markup to rely
        on), and it will NOT work if the login flow includes a CAPTCHA,
        an emailed verification code, or 2FA -- those genuinely require a
        human. Returns True if it looks like login succeeded, False
        otherwise (caller should fall back to the manual-wait flow).
        """
        from utils.logger import logger
        page = self.page

        async def _find_first(selectors):
            for sel in selectors:
                try:
                    loc = page.locator(sel).first
                    if await loc.count() > 0 and await loc.is_visible():
                        return loc
                except Exception:
                    continue
            return None

        email_selectors = [
            "input[type='email']",
            "input[name*='email' i]",
            "input[id*='email' i]",
            "input[autocomplete='username']",
            "input[type='text']",
        ]
        password_selectors = [
            "input[type='password']",
        ]
        submit_selectors = [
            "button[type='submit']",
            "button:has-text('Log in')",
            "button:has-text('Login')",
            "button:has-text('Sign in')",
            "button:has-text('Continue')",
            "input[type='submit']",
        ]

        try:
            logger.info("Attempting automated Intron login...")

            email_field = await _find_first(email_selectors)
            if email_field:
                await email_field.fill(email)
            else:
                logger.warning("Auto-login: couldn't find an email/username field.")
                return False

            # Two-step login flow: email first, password appears after a
            # "Continue" click. If no password field is visible yet, try
            # clicking a continue/submit button once.
            password_field = await _find_first(password_selectors)
            if not password_field:
                btn = await _find_first(submit_selectors)
                if btn:
                    await btn.click()
                    await page.wait_for_timeout(1500)
                password_field = await _find_first(password_selectors)

            if password_field:
                await password_field.fill(password)
            else:
                logger.warning("Auto-login: couldn't find a password field.")
                return False

            submit_btn = await _find_first(submit_selectors)
            if submit_btn:
                await submit_btn.click()
            else:
                await password_field.press("Enter")

            await page.wait_for_timeout(3000)

            if self.is_login_page():
                logger.warning(
                    "Auto-login submitted but still on a login/auth page -- "
                    "credentials may be wrong, or this platform needs a "
                    "verification code/CAPTCHA that can't be automated."
                )
                return False

            logger.info("Auto-login looks successful.")
            return True

        except Exception as e:
            logger.warning(f"Auto-login attempt failed: {e}")
            return False

    async def wait_for_media(self, timeout=90):
        from utils.logger import logger
        logger.info("Waiting for media request...")
        start = time.time()
        while time.time() - start < timeout:
            if self.latest_media_url:
                logger.info("Media request captured.")
                return self.latest_media_url
            await asyncio.sleep(0.25)
        raise RuntimeError("No audio detected on this task page.")

    async def attach_page(self, new_page):
        from utils.logger import logger
        self.page = new_page
        self.page.on("request", self._handle_request)
        logger.info(f"Switched tracking to new page: {new_page.url}")


# --------------------------------------------------
# Async pipeline -- runs everything inside one event loop
# --------------------------------------------------

async def _async_pipeline(task_queue, result_queue):
    """
    All Playwright work happens here, inside a single asyncio event
    loop created by asyncio.run() in the worker thread. No sync API,
    no event-loop conflicts, no NotImplementedError.
    """
    from utils.logger import logger
    import random

    browser = None
    profile = None
    submitter_page = None
    task_number = 1
    model_choice = "Faster-Whisper (base)"
    language_choice = "Auto Detect"

    def emit(step, status, detail=""):
        logger.info(f"[{status.upper()}] {step or 'log'} {detail}")
        result_queue.put(EventMsg(step, status, detail))

    def log(msg):
        logger.info(f"[LOG] log {msg}")
        result_queue.put(EventMsg(None, "log", msg))

    while True:
        try:
            msg = task_queue.get(timeout=600)
        except Exception:
            break

        if isinstance(msg, CloseMsg):
            break

        try:
            # -----------------------------------------------
            # OpenAndUnderstand
            # -----------------------------------------------
            if isinstance(msg, OpenAndUnderstandMsg):
                from urllib.parse import urlparse
                from utils.url_utils import normalize_url

                url = normalize_url(msg.url)
                model_choice = msg.model_choice
                language_choice = msg.language_choice
                domain = urlparse(url).hostname or "default"
                log(f"Platform domain: {domain}")

                emit("Browser Running", "running", "Starting browser...")
                browser = AsyncBrowserManager(domain=domain)
                await browser.start()
                emit("Browser Running", "done", "Browser started")

                emit("Logged In", "running")
                await browser.open_project(url)

                if browser.is_login_page():
                    # Session is stale or missing -- delete it, get a fresh
                    # context (no cookies), then wait for the user to log in
                    # manually in the visible Chromium window.
                    logger.warning("Session stale -- clearing and retrying.")
                    browser.auth.delete_session()
                    await browser.fresh_context()
                    await browser.open_project(url)

                    if browser.is_login_page():
                        import os
                        intron_email = os.getenv("INTRON_EMAIL")
                        intron_password = os.getenv("INTRON_PASSWORD")

                        auto_logged_in = False
                        if intron_email and intron_password:
                            emit("Logged In", "running", "Attempting automated login...")
                            auto_logged_in = await browser.attempt_auto_login(
                                intron_email, intron_password
                            )
                            if auto_logged_in:
                                await browser.open_project(url)
                                auto_logged_in = not browser.is_login_page()

                        if not auto_logged_in:
                            # Tell the user to log in, then WAIT here (up to
                            # 5 minutes) watching for the URL to change away
                            # from the login page. Don't error immediately.
                            if intron_email and intron_password:
                                msg_text = (
                                    f"Automated login for {domain} didn't succeed "
                                    "(credentials may be wrong, or this platform "
                                    "needs a verification step that can't be "
                                    "automated). Waiting in case it completes "
                                    "another way..."
                                )
                            else:
                                msg_text = (
                                    f"Login required for {domain}, but no "
                                    "INTRON_EMAIL/INTRON_PASSWORD are configured "
                                    "for automated login. Set them in your "
                                    "environment/secrets, or log in manually if "
                                    "you can see the browser (local, non-headless "
                                    "runs only)."
                                )
                            emit("Logged In", "running", msg_text)
                            logger.info("Waiting for login (up to 5 minutes)...")

                            page = browser.get_page()
                            login_timeout = 300  # 5 minutes
                            start_wait = time.time()
                            logged_in = False

                            while time.time() - start_wait < login_timeout:
                                await asyncio.sleep(2)
                                try:
                                    current_url = page.url.lower()
                                    if not any(k in current_url for k in ("login", "signin", "sign-in", "auth")):
                                        logged_in = True
                                        break
                                except Exception:
                                    pass

                            if not logged_in:
                                msg_text = "Login timed out after 5 minutes. Click Retry to try again."
                                emit("Logged In", "error", msg_text)
                                result_queue.put(ErrorMsg(msg_text))
                                continue

                            logger.info("Login detected! Continuing...")
                        else:
                            logger.info("Auto-login succeeded, continuing...")

                emit("Logged In", "done", "Project page opened")
                await browser.save_session()

                # Read instructions
                emit("Project Loaded", "running", "Reading instructions...")

                from automation.instructions.instruction_analyzer import InstructionAnalyzer
                from automation.project.project_profile import ProjectProfile

                page = browser.get_page()
                title = await page.title()

                body = await page.evaluate("document.body.innerText")

                profile = ProjectProfile()
                profile.platform = domain
                profile.title = title or "Untitled Project"
                profile.description = body
                profile.instructions = body

                # Try structured sections
                structured = []
                for selector, label in [("#dos","DOS"), ("#dont","DON'TS"), ("#howToWork","HOW TO USE")]:
                    try:
                        el = await page.query_selector(selector)
                        if el:
                            text = await el.inner_text()
                            if text:
                                structured.append(f"=== {label} ===\n{text}")
                    except Exception:
                        pass
                if structured:
                    profile.instructions = body + "\n\n" + "\n\n".join(structured)

                profile = InstructionAnalyzer().analyze(profile)

                log(f"Understood rules -- language: {profile.language or 'n/a'}, task: {profile.task_type or 'n/a'}")

                # Navigate to task
                log("Entering task...")
                browser.clear_media_requests()

                # Scroll to bottom and wait for button to be visible
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(3000)

                # Find Start button - try multiple times with increasing waits
                start_clicked = False
                start_selectors = [
                    'a:has-text("Start Transcribing")',
                    'button:has-text("Start Transcribing")',
                    'a:has-text("Good Luck")',
                    'button:has-text("Good Luck")',
                    'a:has-text("Start")',
                    'button:has-text("Start")',
                    '[class*="goDashboard"]',
                    '[class*="start"]',
                ]

                for attempt in range(3):
                    if attempt > 0:
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await page.wait_for_timeout(2000)

                    for selector in start_selectors:
                        try:
                            el = await page.query_selector(selector)
                            if not el:
                                continue
                            log(f"Clicking: {selector}")
                            # Try watching for new tab first
                            try:
                                async with page.context.expect_page(timeout=4000) as new_page_info:
                                    await el.click()
                                new_page = await new_page_info.value
                                await new_page.wait_for_load_state("domcontentloaded", timeout=30000)
                                await browser.attach_page(new_page)
                                page = new_page
                            except Exception:
                                # No new tab -- same-page navigation
                                try:
                                    await el.click()
                                except Exception:
                                    pass
                                await asyncio.sleep(2)

                            start_clicked = True
                            break
                        except Exception:
                            continue

                    if start_clicked:
                        break

                if not start_clicked:
                    raise RuntimeError(
                        "Could not find the Start Transcribing button. "
                        "Make sure you pasted the instruction page URL, "
                        "not a task URL."
                    )

                # Wait for task page
                try:
                    await page.wait_for_selector(
                        "textarea, [contenteditable='true'], audio",
                        timeout=60000
                    )
                except Exception:
                    pass

                submitter_page = page
                task_number = 1
                emit("Project Loaded", "done", "Task 1 opened")
                result_queue.put(ResultMsg(profile))

            # -----------------------------------------------
            # Transcribe
            # -----------------------------------------------
            elif isinstance(msg, TranscribeMsg):
                if browser is None:
                    result_queue.put(ErrorMsg("No browser running."))
                    continue

                emit("Audio Downloaded", "running", "Waiting for audio...")
                media_url = await browser.wait_for_media(timeout=90)

                # Download audio -- use requests (always available) via
                # asyncio executor so it doesn't block the event loop
                import os
                os.makedirs("downloads", exist_ok=True)
                filename = media_url.split("/")[-1].split("?")[0]
                local_path = os.path.join("downloads", filename)

                def _download_sync(url, path):
                    import requests
                    r = requests.get(url, timeout=60)
                    r.raise_for_status()
                    with open(path, "wb") as f:
                        f.write(r.content)

                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, _download_sync, media_url, local_path)

                emit("Audio Downloaded", "done", f"Saved: {local_path}")

                # Transcribe
                provider_label = model_choice

                # Language: use manual selection > profile detected > auto-detect
                # Never use empty string -- Faster-Whisper crashes on that
                safe_lang = None
                if language_choice and language_choice not in ("Auto Detect", ""):
                    safe_lang = language_choice
                elif profile and profile.language:
                    safe_lang = profile.language

                # Map common full names to Whisper language codes
                lang_map = {
                    "French": "fr", "English": "en", "Spanish": "es",
                    "Arabic": "ar", "Portuguese": "pt", "Swahili": "sw",
                    "Oromo": "or", "Amharic": "am", "Hausa": "ha",
                }
                if safe_lang and safe_lang in lang_map:
                    safe_lang = lang_map[safe_lang]

                # IMPORTANT: transcription = speech-to-text in the ORIGINAL
                # language. Never translate unless the user explicitly asked
                # for translation via the task_type. The keyword fallback
                # often wrongly sets translate=True when instructions say
                # "do not translate" -- override it here.
                should_translate = (
                    profile is not None
                    and getattr(profile, "task_type", "") == "Translation"
                    and getattr(profile, "translate", False)
                )

                if profile:
                    profile.translate = should_translate

                emit("Transcribing...", "running",
                     f"Using {provider_label}" + (f" | lang: {safe_lang}" if safe_lang else " | auto-detect"))

                from speech.speech_manager import SpeechManager
                result = SpeechManager(provider_label=provider_label).transcribe(
                    audio_file=local_path,
                    language=safe_lang,
                    profile=profile,
                )

                if not result.success:
                    emit("Transcribing...", "error", result.error)
                    result_queue.put(ErrorMsg(result.error))
                    continue

                emit("Transcribing...", "done", "Transcript ready")
                result_queue.put(ResultMsg(result.transcript))

            # -----------------------------------------------
            # Fill transcript
            # -----------------------------------------------
            elif isinstance(msg, FillTranscriptMsg):
                if submitter_page is None:
                    result_queue.put(ErrorMsg("No task page."))
                    continue

                text = msg.text
                for selector in [
                    "textarea[placeholder*='verbatim']",
                    "textarea[placeholder*='text here']",
                    "textarea[placeholder*='transcri']",
                    "textarea",
                    "[contenteditable='true']",
                ]:
                    try:
                        el = await submitter_page.query_selector(selector)
                        if el:
                            await el.click()
                            await submitter_page.keyboard.press("Control+a")
                            await submitter_page.keyboard.press("Delete")
                            # Type at human speed
                            for i, char in enumerate(text):
                                delay = random.randint(60, 120)
                                if char in " \n":
                                    delay = random.randint(80, 180)
                                elif char in ".,!?;:":
                                    delay = random.randint(100, 200)
                                await submitter_page.keyboard.type(char)
                                await asyncio.sleep(delay / 1000)
                                if i > 0 and i % random.randint(40, 80) == 0:
                                    await asyncio.sleep(random.randint(300, 700) / 1000)
                            emit("Typing Transcript", "done")
                            result_queue.put(ResultMsg("filled"))
                            break
                    except Exception:
                        continue
                else:
                    result_queue.put(ErrorMsg("Could not find transcript field."))

            # -----------------------------------------------
            # Submit (edited transcript) & advance to next task
            # -----------------------------------------------
            elif isinstance(msg, SubmitMsg):
                if submitter_page is None:
                    result_queue.put(ErrorMsg("No task page."))
                    continue

                text = msg.text

                # Re-fill the field with the (possibly user-edited) text,
                # since the user may have changed it in the review box.
                filled = False
                for selector in [
                    "textarea[placeholder*='verbatim']",
                    "textarea[placeholder*='text here']",
                    "textarea[placeholder*='transcri']",
                    "textarea",
                    "[contenteditable='true']",
                ]:
                    try:
                        el = await submitter_page.query_selector(selector)
                        if el:
                            await el.click()
                            await submitter_page.keyboard.press("Control+a")
                            await submitter_page.keyboard.press("Delete")
                            await submitter_page.keyboard.type(text)
                            filled = True
                            break
                    except Exception:
                        continue

                if not filled:
                    result_queue.put(ErrorMsg("Could not find transcript field to submit."))
                    continue

                emit("Submitting", "running", "Clicking submit on the platform...")

                submitted = False
                for sel in [
                    "button[type='submit']",
                    "button:has-text('Submit')",
                    "button:has-text('Save')",
                    "button:has-text('Continue')",
                    "button:has-text('Next')",
                    "input[type='submit']",
                ]:
                    try:
                        el = await submitter_page.query_selector(sel)
                        if el:
                            await el.click()
                            submitted = True
                            break
                    except Exception:
                        continue

                if not submitted:
                    result_queue.put(ErrorMsg(
                        "Typed the transcript but couldn't find a Submit button "
                        "to click automatically."
                    ))
                    continue

                try:
                    await submitter_page.wait_for_load_state("networkidle", timeout=15000)
                except Exception:
                    pass
                await asyncio.sleep(2)

                emit("Submitting", "done", "Submitted")

                # Detect whether a next task loaded automatically; if not,
                # try clicking whatever advances to it.
                browser.clear_media_requests()
                has_next = False
                try:
                    el = await submitter_page.query_selector("textarea, [contenteditable='true']")
                    has_next = el is not None
                except Exception:
                    pass

                if not has_next:
                    for sel in ['button:has-text("Next")', 'button:has-text("Skip")']:
                        try:
                            el = await submitter_page.query_selector(sel)
                            if el:
                                await el.click()
                                await asyncio.sleep(2)
                                el2 = await submitter_page.query_selector("textarea, [contenteditable='true']")
                                has_next = el2 is not None
                                if has_next:
                                    break
                        except Exception:
                            continue

                if has_next:
                    task_number += 1

                result_queue.put(ResultMsg(has_next))

            # -----------------------------------------------
            # Next task
            # -----------------------------------------------
            elif isinstance(msg, NextTaskMsg):
                browser.clear_media_requests()
                # Check if next task is present
                has_next = False
                try:
                    el = await submitter_page.query_selector("textarea, [contenteditable='true']")
                    has_next = el is not None
                except Exception:
                    pass

                if not has_next:
                    # Try clicking Next button
                    for sel in ['button:has-text("Next")', 'button:has-text("Skip")']:
                        try:
                            el = await submitter_page.query_selector(sel)
                            if el:
                                await el.click()
                                await asyncio.sleep(2)
                                el2 = await submitter_page.query_selector("textarea, [contenteditable='true']")
                                has_next = el2 is not None
                                if has_next:
                                    break
                        except Exception:
                            continue

                if has_next:
                    task_number += 1
                result_queue.put(ResultMsg(has_next))

        except Exception as e:
            result_queue.put(ErrorMsg(f"{e}\n{traceback.format_exc()}"))

    # Clean shutdown
    if browser:
        try:
            await browser.close()
        except Exception:
            pass


# --------------------------------------------------
# Thread entry point
# --------------------------------------------------

def _worker_main(task_queue, result_queue):
    """
    Creates a fresh ProactorEventLoop on this thread and runs the
    entire async pipeline inside it. No sync Playwright, no event-loop
    conflicts, works on Windows Python 3.9.
    """
    if sys.platform.startswith("win"):
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(_async_pipeline(task_queue, result_queue))
    finally:
        loop.close()


# --------------------------------------------------
# Handle used from Streamlit
# --------------------------------------------------

class BrowserProcess:

    def __init__(self):
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self._thread = threading.Thread(
            target=_worker_main,
            args=(self.task_queue, self.result_queue),
            daemon=True,
            name="PlaywrightWorker",
        )
        self._thread.start()

    def is_alive(self):
        return self._thread.is_alive()

    def _send_and_wait(self, msg, timeout=300):
        self.task_queue.put(msg)
        events = []
        deadline = time.time() + timeout

        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                raise RuntimeError(
                    f"Operation timed out after {timeout}s. "
                    "The browser is still running -- click STOP then START again."
                )
            try:
                item = self.result_queue.get(timeout=min(remaining, 1.0))
            except queue.Empty:
                if not self._thread.is_alive():
                    raise RuntimeError(
                        "Browser worker stopped unexpectedly. "
                        "Click STOP then START again."
                    )
                # Thread alive but no result yet -- keep waiting
                continue

            if isinstance(item, EventMsg):
                events.append(item)
            elif isinstance(item, ResultMsg):
                return item.value, events
            elif isinstance(item, ErrorMsg):
                raise RuntimeError(item.message)

    def open_and_understand(self, url, model_choice, language_choice, timeout=600):
        return self._send_and_wait(
            OpenAndUnderstandMsg(url, model_choice, language_choice), timeout=timeout)

    def transcribe(self):
        return self._send_and_wait(TranscribeMsg(), timeout=300)

    def fill_transcript(self, text):
        return self._send_and_wait(FillTranscriptMsg(text), timeout=300)

    def submit(self, text):
        return self._send_and_wait(SubmitMsg(text), timeout=60)

    def next_task(self):
        return self._send_and_wait(NextTaskMsg(), timeout=60)

    def close(self):
        try:
            self.task_queue.put(CloseMsg())
            self._thread.join(timeout=10)
        except Exception:
            pass
