from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from browser.browser_manager import BrowserManager
from automation.project.project_reader import ProjectReader
from automation.project.project_navigator import ProjectNavigator
from automation.project.task_submitter import TaskSubmitter
from audio.audio_downloader import AudioDownloader
from speech.speech_manager import SpeechManager
from speech.provider_factory import DEFAULT_MODEL, PROVIDER_CONFIGS
from utils.logger import logger
from utils.url_utils import normalize_url


class NoTasksAvailable(Exception):
    """Raised when the project has no tasks to work on right now."""
    pass

# The exact status checklist shown in the UI, in display order.
STATUS_KEYS = [
    "Browser Running",
    "Logged In",
    "Project Loaded",
    "Audio Downloaded",
    "Transcribing...",
    "Typing Transcript",
    "Waiting...",
]

PROVIDER_MAP = {}  # kept for backward compat, now unused


class PipelineEngine:

    def __init__(self, on_step=None, model_choice=DEFAULT_MODEL, language_choice="Auto Detect"):
        self.browser = BrowserManager()
        self.page = None
        self.profile = None
        self.submitter = None
        self.task_number = 0

        # Events are collected here (plain list, safe to touch from any
        # thread) instead of calling a Streamlit-session-touching
        # callback directly -- st.session_state is not safe to mutate
        # from a background thread and doing so can hang the app. The
        # UI drains this list into session_state itself, from the main
        # Streamlit thread, after each call into the engine returns.
        self.events = []
        self.on_step = on_step  # optional extra hook; failures here are swallowed

        self.provider_label = model_choice
        self.language_choice = None if language_choice == "Auto Detect" else language_choice

    def _report(self, step, status, detail=""):
        logger.info(f"[{status.upper()}] {step or 'log'} {detail}")
        self.events.append((step, status, detail))
        if self.on_step:
            try:
                self.on_step(step, status, detail)
            except Exception:
                pass

    def _log(self, message):
        self._report(None, "log", message)

    def _looks_like_login_page(self):
        try:
            return self.page.locator("input[type='password']").count() > 0
        except Exception:
            return False

    def _init_browser_for_url(self, url):
        """Create a domain-aware browser so each platform keeps its own session."""
        from urllib.parse import urlparse
        from browser.session_storage import SessionStorage
        domain = urlparse(url).hostname or "default"
        self._log(f"Platform domain: {domain}")
        self.browser = BrowserManager(domain=domain)

    # --------------------------------------------------
    # Open -> Read -> Understand -> Click Start -> Open First Task
    # --------------------------------------------------

    def open_and_understand(self, url):
        url = normalize_url(url)

        self._init_browser_for_url(url)

        self._report("Browser Running", "running", "Starting browser...")
        self.browser.start()
        self._report("Browser Running", "done", "Browser started")

        self.browser.open_project(url)
        self.page = self.browser.get_page()

        if self._looks_like_login_page():
            # Session is stale -- delete it, create a fresh browser
            # context (the old one still holds the expired cookies),
            # then navigate again.
            logger.warning("Session appears stale -- clearing and retrying with fresh context.")
            try:
                self.browser.auth.delete_session()
            except Exception:
                pass

            try:
                self.page = self.browser.fresh_context()
                self.browser.open_project(url)
                self.page = self.browser.get_page()
            except Exception:
                pass

            if self._looks_like_login_page():
                domain = self.browser.domain
                message = (
                    f"Showing login page for {domain}. "
                    "Please log in manually in the Chromium window, "
                    "then click Retry — the tool will remember your "
                    "session and go straight to work next time."
                )
                self._report("Logged In", "error", message)
                raise RuntimeError(message)

        self._report("Logged In", "done", "Project page opened")

        try:
            self.browser.save_session()
        except Exception:
            pass

        self._report("Project Loaded", "running", "Reading instructions...")

        reader = ProjectReader(self.page)
        self.profile = reader.read()

        self._log(
            f"Understood rules -- language: {self.profile.language or 'n/a'}, "
            f"task: {self.profile.task_type or 'n/a'}"
        )

        # Clear any media captured during instruction-page load BEFORE
        # clicking Start -- audio detected after this point belongs to
        # the actual task, not to the instruction page.
        self.browser.clear_media_requests()

        navigator = ProjectNavigator(self.page)
        task_page, opened_new_tab = navigator.enter_task()

        if opened_new_tab:
            self.page = self.browser.attach_page(task_page)
            self._log(f"Task opened in a new tab: {self.page.url}")
        else:
            self.page = task_page

        self._log("Clicked Good Luck / Start")

        # Do NOT clear media requests here -- the audio URL may have
        # already been captured during page navigation above.
        self.submitter = TaskSubmitter(self.page)

        if not self.submitter.has_next_task():
            message = (
                "There don't seem to be any tasks to work on in this project "
                "right now. Please check back later, or try a different project."
            )
            self._report("Project Loaded", "done", "No tasks available")
            self._log(f"📭 {message}")
            raise NoTasksAvailable(message)

        self.task_number = 1

        self._report("Project Loaded", "done", "Task 1 opened")

        return self.profile

    # --------------------------------------------------
    # Transcribe
    # --------------------------------------------------

    def transcribe_current_task(self):
        self._report("Audio Downloaded", "running", "Waiting for audio...")

        try:
            media_url = self.browser.wait_for_media_request(timeout=90)
        except PlaywrightTimeoutError:
            self._report("Audio Downloaded", "error", "No audio detected on this task page.")
            raise

        download = AudioDownloader().download(media_url)

        if not download.success:
            self._report("Audio Downloaded", "error", download.message)
            raise RuntimeError(download.message)

        self._report("Audio Downloaded", "done", f"Saved: {download.local_path}")

        self._report("Transcribing...", "running", f"Using {self.provider_name}")

        result = SpeechManager(provider_label=self.provider_label).transcribe(
            audio_file=download.local_path,
            instructions=self.profile.instructions if self.profile else None,
            language=self.language_choice or (self.profile.language if self.profile else None) or None,
            profile=self.profile,
        )

        if not result.success:
            self._report("Transcribing...", "error", result.error)
            raise RuntimeError(result.error)

        self._report("Transcribing...", "done", "Transcript ready")

        for warning in getattr(result, "warnings", []) or []:
            self._log(f"⚠ {warning}")

        return result.transcript

    # --------------------------------------------------
    # Submit + advance to Next Task
    # --------------------------------------------------

    def submit_current_task(self, final_text):
        self._report("Typing Transcript", "running")
        self.submitter.fill_transcript(final_text)
        self._report("Typing Transcript", "done")

        self._report("Waiting...", "running", "Submitting...")
        self.submitter.submit()

        self.browser.clear_media_requests()

        has_next = self.submitter.has_next_task()

        if has_next:
            self.task_number += 1
            self._report("Waiting...", "done", f"Task {self.task_number} loaded")
        else:
            self._report("Waiting...", "done", "No more tasks -- all done!")

        return has_next

    # --------------------------------------------------
    # Shutdown
    # --------------------------------------------------

    def close(self):
        try:
            self.browser.save_session()
        except Exception:
            pass
        self.browser.close()
