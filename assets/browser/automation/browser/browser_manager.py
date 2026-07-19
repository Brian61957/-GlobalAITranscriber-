from playwright.sync_api import sync_playwright, TimeoutError

from browser.auth_manager import AuthManager
from utils.logger import logger


class BrowserManager:

    def __init__(self):

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        self.auth = AuthManager()

    # --------------------------------------------------
    # Browser Lifecycle
    # --------------------------------------------------

    def start(self):

        # Browser already running
        if self.page is not None:

            logger.info("Browser already running.")

            return self.page

        logger.info("Starting browser...")

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=False
        )

        if self.auth.has_saved_session():

            logger.info("Loading saved browser session...")

            self.context = self.browser.new_context(
                storage_state=self.auth.session_path()
            )

        else:

            logger.info("No saved session found.")

            self.context = self.browser.new_context()

        self.page = self.context.new_page()

        return self.page

    # --------------------------------------------------
    # Navigation
    # --------------------------------------------------

    def open_project(self, project_url):

        if self.page is None:

            self.start()

        logger.info("Opening project...")

        try:

            self.page.goto(
                project_url,
                wait_until="domcontentloaded",
                timeout=60000
            )

        except TimeoutError:

            logger.warning(
                "Navigation timed out. Continuing with current page..."
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

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def get_page(self):

        return self.page

    def is_running(self):

        return self.page is not None

    # --------------------------------------------------
    # Session
    # --------------------------------------------------

    def save_session(self):

        if self.context is None:

            return

        logger.info("Saving browser session...")

        self.context.storage_state(
            path=self.auth.session_path()
        )

        logger.info("Session saved successfully.")

    # --------------------------------------------------
    # Convenience
    # --------------------------------------------------

    def open(self, url):

        self.start()

        return self.open_project(url)

    # --------------------------------------------------
    # Shutdown
    # --------------------------------------------------

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