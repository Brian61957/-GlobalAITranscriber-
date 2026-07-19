from playwright.sync_api import TimeoutError

from browser.page_scanner import PageScanner
from actions.action_engine import ActionEngine
from utils.logger import logger


class ProjectNavigator:

    # Kept as a last-resort fallback in case the Smart Action Engine
    # (snapshot + live DOM search) can't reach the page for some reason.
    START_BUTTONS = [

        "Good Luck",
        "Start",
        "Continue",
        "Proceed",
        "Begin"

    ]

    def __init__(self, page):

        self.page = page
        self.engine = ActionEngine()

    # --------------------------------------------------
    # Fallback Find (only used if the Smart Action Engine raises)
    # --------------------------------------------------

    def _find_start_button_fallback(self):

        for name in self.START_BUTTONS:

            try:

                button = self.page.get_by_role(
                    "button",
                    name=name,
                    exact=False
                )

                if button.count():

                    logger.info(f"Fallback found button: {name}")

                    return button.first

            except Exception:

                pass

        return None

    # --------------------------------------------------
    # Enter Task
    # --------------------------------------------------

    def enter_task(self):

        logger.info("=" * 60)
        logger.info("ENTERING TASK")
        logger.info("=" * 60)

        context = self.page.context
        new_page = None

        try:

            with context.expect_page(timeout=8000) as new_page_info:

                self._click_start_button()

            new_page = new_page_info.value

            new_page.wait_for_load_state("domcontentloaded", timeout=30000)

            logger.info(f"A new tab opened for the task: {new_page.url}")

            self.page = new_page

        except TimeoutError:

            logger.info("No new tab opened -- assuming the click navigates within the same page.")

        try:

            self.page.wait_for_load_state("networkidle", timeout=30000)

        except TimeoutError:

            logger.warning("Network idle timeout.")

        self.wait_for_task()

        logger.info("Task page loaded.")

        return self.page, new_page is not None

    def _click_start_button(self):

        # Guard: abort if we're on a login/auth page -- this works
        # for any platform, not just Intron
        current_url = self.page.url.lower()
        page_title = ""
        try:
            page_title = self.page.title().lower()
        except Exception:
            pass

        is_login = (
            any(kw in current_url for kw in ("login", "signin", "sign-in", "auth", "account/login"))
            or any(kw in page_title for kw in ("login", "sign in", "log in"))
            or self.page.locator("input[type='password']").count() > 0
        )

        if is_login:
            raise RuntimeError(
                "The browser is on a login page. "
                "Please log in manually, then click Retry."
            )

        try:

            # Scroll to the bottom first -- "Start Transcribing" is at
            # the very bottom of the instruction page.
            logger.info("Scrolling to bottom of instruction page...")
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(2000)

            snapshot = PageScanner(self.page).scan()

            candidates = [b for b in snapshot.buttons if b.role == "start_button"]

            logger.info(f"Found {len(candidates)} candidate(s) tagged 'start_button':")
            for c in candidates:
                logger.info(f"  - text='{c.text}' tag='{c.tag}' aria_label='{c.aria_label}' href='{c.href}' selector='{c.selector}'")

            # Also dump ALL buttons/links found so we can see what the
            # scanner actually sees on this page.
            all_interactive = [b for b in snapshot.buttons if b.text.strip() or b.aria_label.strip()]
            logger.info(f"All {len(all_interactive)} interactive elements with text:")
            for b in all_interactive[:30]:
                logger.info(f"  [{b.tag}] role='{b.role}' text='{b.text}' aria='{b.aria_label}' href='{b.href}'")

            try:
                import os
                os.makedirs("debug_screenshots", exist_ok=True)
                self.page.screenshot(path="debug_screenshots/before_click.png", full_page=True)
                logger.info("Screenshot saved: debug_screenshots/before_click.png")
            except Exception as e:
                logger.warning(f"Could not save before-click screenshot: {e}")

            # Raw DOM dump -- queries every possible interactive element
            # type so we can identify exactly what "Start Transcribing" is.
            logger.info("=== RAW DOM DUMP (all interactive elements) ===")
            raw_elements = self.page.evaluate("""() => {
                const selectors = [
                    'button', 'a', '[role="button"]', '[role="link"]',
                    'input[type="submit"]', 'input[type="button"]',
                    '[onclick]', '[data-action]', '.btn', '.button',
                    '[class*="btn"]', '[class*="button"]'
                ];
                const seen = new Set();
                const results = [];
                for (const sel of selectors) {
                    try {
                        const els = document.querySelectorAll(sel);
                        for (const el of els) {
                            const text = (el.innerText || el.value || el.getAttribute('aria-label') || '').trim();
                            const key = el.tagName + text;
                            if (!seen.has(key) && text) {
                                seen.add(key);
                                results.push({
                                    tag: el.tagName,
                                    text: text.substring(0, 80),
                                    role: el.getAttribute('role') || '',
                                    className: el.className.substring(0, 60),
                                    href: el.getAttribute('href') || '',
                                    onclick: el.getAttribute('onclick') || '',
                                });
                            }
                        }
                    } catch(e) {}
                }
                return results;
            }""")
            logger.info(f"Found {len(raw_elements)} unique interactive elements:")
            for el in raw_elements:
                logger.info(f"  <{el['tag']}> text='{el['text']}' role='{el['role']}' class='{el['className']}' href='{el['href']}'")
            logger.info("=== END RAW DOM DUMP ===")

            self.engine.click(self.page, snapshot, "start_button")

            logger.info("Start button clicked (via Smart Action Engine).")

        except Exception as e:

            logger.warning(f"Smart Action Engine could not click start button ({e}); trying fallback.")

            button = self._find_start_button_fallback()

            if button is None:

                raise RuntimeError("Could not locate the Start/Good Luck button.")

            button.scroll_into_view_if_needed()
            button.click()

            logger.info("Start button clicked (via fallback).")

    # --------------------------------------------------
    # Wait For Task
    # --------------------------------------------------

    def wait_for_task(self):

        logger.info("Waiting for transcription page...")

        try:

            logger.info(f"Current URL: {self.page.url}")

        except Exception:

            pass

        # One combined wait instead of several rigid sequential ones --
        # succeeds as soon as ANY of these appear, and includes
        # contenteditable divs (which PageScanner/ActionEngine already
        # treat as valid transcript boxes elsewhere, but this method
        # previously didn't check for at all).
        interactive_selectors = "textarea, [contenteditable='true'], input[type='text'], button"

        try:

            self.page.locator(interactive_selectors).first.wait_for(
                state="visible",
                timeout=45000
            )

            logger.info("Task page ready (interactive element visible).")

            self._log_page_snapshot()

            return

        except Exception:

            logger.warning("No visible interactive element yet -- checking for an audio element as a fallback signal.")

        # Native <audio> elements are very often kept hidden while a
        # custom player UI is built around them, so don't require
        # visibility for this check -- just that it's in the DOM at all.
        try:

            self.page.locator("audio").first.wait_for(
                state="attached",
                timeout=15000
            )

            logger.info("Task page ready (audio element attached).")

            self._log_page_snapshot()

            return

        except Exception:

            pass

        self._log_page_snapshot(level="warning")

        raise RuntimeError(
            "The task page never appeared after clicking Start. "
            f"Still on: {self._safe_url()} -- title: '{self._safe_title()}'. "
            "The button click may have opened a confirmation step, a "
            "permissions prompt, or a slow-loading page this app doesn't "
            "recognize yet."
        )

    def _safe_url(self):
        try:
            return self.page.url
        except Exception:
            return "unknown"

    def _safe_title(self):
        try:
            return self.page.title()
        except Exception:
            return "unknown"

    def _log_page_snapshot(self, level="info"):
        try:
            url = self.page.url
            title = self.page.title()
            body_text = self.page.locator("body").inner_text()[:300].replace("\n", " ")
        except Exception as e:
            logger.warning(f"Could not capture page diagnostics: {e}")
            return

        log_fn = logger.warning if level == "warning" else logger.info
        log_fn(f"Page URL: {url}")
        log_fn(f"Page title: {title}")
        log_fn(f"Page text (first 300 chars): {body_text}")
