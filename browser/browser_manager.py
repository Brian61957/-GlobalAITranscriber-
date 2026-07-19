import time

from playwright.sync_api import sync_playwright, TimeoutError

from browser.auth_manager import AuthManager
from utils.logger import logger
from utils.url_utils import normalize_url


class BrowserManager:

    def __init__(self, domain: str = "default"):

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.domain = domain

        # Per-domain session storage -- each platform gets its own
        # session file so logins never overwrite each other
        from browser.session_storage import SessionStorage
        self.session_storage = SessionStorage(domain)
        self.auth = AuthManager(self.session_storage)

        # ------------------------------------------
        # Network Monitoring
        # ------------------------------------------

        self.requests = []

        self.media_requests = []

        self.latest_media_url = None

        self.media_extensions = (

            ".wav",
            ".mp3",
            ".ogg",
            ".m4a",
            ".aac",
            ".flac",
            ".opus"

        )

    # ==================================================
    # Browser Lifecycle
    # ==================================================

    def start(self):

        if self.page is not None:

            logger.info("Browser already running.")

            return self.page

        if self.playwright is not None:

            logger.warning("Browser launch already in progress or partially completed -- not relaunching.")

            return self.page

        logger.info("Starting browser...")

        logger.info("Step 1/4: launching Playwright driver...")
        self.playwright = sync_playwright().start()
        logger.info("Step 1/4 done: Playwright driver launched.")

        logger.info("Step 2/4: launching Chromium (headless, for cloud deployment)...")
        self.browser = self.playwright.chromium.launch(
            headless=True
        )
        logger.info("Step 2/4 done: Chromium launched.")

        logger.info("Step 3/4: creating browser context...")

        if self.auth.has_saved_session():

            logger.info("Loading saved browser session...")

            self.context = self.browser.new_context(

                storage_state=self.auth.session_path()

            )

        else:

            logger.info("No saved session found.")

            self.context = self.browser.new_context()

        logger.info("Step 3/4 done: browser context created.")

        logger.info("Step 4/4: opening a new page...")
        self.page = self.context.new_page()
        logger.info("Step 4/4 done: page opened.")

        self._attach_network_monitor(self.page)

        return self.page

    def _attach_network_monitor(self, page):
        page.on(
            "request",
            self._handle_request
        )

        logger.info("Network monitor started.")

    def attach_page(self, new_page):
        """
        Switches tracking to a different Page object -- needed when a
        click opens the actual task in a new browser tab rather than
        navigating the current one (common for target="_blank" buttons).
        Without this, audio detection would keep listening on the old,
        now-irrelevant tab.
        """
        self.page = new_page
        self._attach_network_monitor(new_page)
        logger.info(f"Switched tracking to new page: {new_page.url}")
        return self.page

    def fresh_context(self):
        """
        Tears down the current browser context (which holds the stale
        expired cookies) and creates a brand-new, empty one on the same
        already-running Chromium instance. Called after deleting a stale
        session file so the retry navigates with genuinely fresh cookies
        instead of the same expired ones.
        """
        logger.info("Creating a fresh browser context (clearing expired session)...")

        try:
            if self.page:
                self.page.close()
        except Exception:
            pass

        try:
            if self.context:
                self.context.close()
        except Exception:
            pass

        self.page = None
        self.context = None
        self.media_requests.clear()
        self.latest_media_url = None

        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self._attach_network_monitor(self.page)

        logger.info("Fresh context ready.")
        return self.page

    # ==================================================
    # Network Observer
    # ==================================================

    def _handle_request(self, request):

        try:

            url = request.url

            self.requests.append(url)

            lower = url.lower()

            if lower.endswith(self.media_extensions):

                self.media_requests.append(url)

                self.latest_media_url = url

                logger.info(
                    f"MEDIA DETECTED: {url}"
                )

        except Exception as e:

            logger.warning(
                f"Request observer error: {e}"
            )

    # ==================================================
    # Navigation
    # ==================================================

    def open_project(self, project_url):

        if self.page is None:

            self.start()

        logger.info("Opening project...")

        self.clear_media_requests()

        project_url = normalize_url(project_url)

        try:

            self.page.goto(

                project_url,

                wait_until="domcontentloaded",

                timeout=60000

            )

        except TimeoutError:

            logger.warning(

                "Navigation timed out."

            )

        except Exception as e:

            raise RuntimeError(

                f"Couldn't open '{project_url}'. Double-check it's the "

                f"correct instruction page link. (Details: {e})"

            )

        self.page.wait_for_timeout(2000)

        ready_selectors = [

            "textarea",

            "button",

            "audio",

            "body"

        ]

        for selector in ready_selectors:

            try:

                self.page.wait_for_selector(

                    selector,

                    timeout=5000

                )

                logger.info(

                    f"Page ready ({selector})"

                )

                break

            except TimeoutError:

                pass

        logger.info("Project opened successfully.")

        return self.page

    # ==================================================
    # Media API
    # ==================================================

    def clear_media_requests(self):

        self.media_requests.clear()

        self.latest_media_url = None

    def get_latest_media_url(self):

        return self.latest_media_url

    def get_media_requests(self):

        return list(self.media_requests)

    def wait_for_media_request(

        self,

        timeout=20

    ):

        logger.info(

            "Waiting for media request..."

        )

        start = time.time()

        while time.time() - start < timeout:

            if self.latest_media_url:

                logger.info(

                    "Media request captured."

                )

                return self.latest_media_url

            self.page.wait_for_timeout(250)

        raise TimeoutError(

            "No media request detected."

        )

    # ==================================================
    # Helpers
    # ==================================================

    def get_page(self):

        return self.page

    def is_running(self):

        return self.page is not None

    # ==================================================
    # Session
    # ==================================================

    def save_session(self):

        if self.context is None:

            return

        logger.info("Saving browser session...")

        self.context.storage_state(

            path=self.auth.session_path()

        )

        logger.info(

            "Session saved successfully."

        )

    # ==================================================
    # Convenience
    # ==================================================

    def open(self, url):

        self.start()

        return self.open_project(url)

    # ==================================================
    # Shutdown
    # ==================================================

    def close(self):

        logger.info("Closing browser...")

        if self.browser:

            self.browser.close()

        if self.playwright:

            self.playwright.stop()

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        self.requests.clear()
        self.media_requests.clear()
        self.latest_media_url = None