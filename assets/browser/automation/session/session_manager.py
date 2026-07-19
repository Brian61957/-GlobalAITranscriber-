from automation.session.login_checker import LoginChecker
from automation.session.project_loader import ProjectLoader
from automation.session.clip_locator import ClipLocator
from automation.session.session_state import SessionState

from recovery.recovery_manager import RecoveryManager

from utils.logger import logger


class SessionManager:

    def __init__(self, browser):

        self.browser = browser

        self.state = SessionState()

        self.login = LoginChecker()

        self.loader = ProjectLoader(browser)

        self.locator = ClipLocator()

        self.recovery = RecoveryManager(browser)

    # --------------------------------------------------
    # Start Session
    # --------------------------------------------------

    def start(self, url):

        logger.info("Starting Intron session...")

        # Ensure browser exists
        self.browser.start()

        # Open project and read its contents
        project = self.loader.load(url)

        # Check login status
        logged_in = self.login.check(
            self.browser.get_page()
        )

        # Recover session if necessary
        recovery_result = None

        if not logged_in:

            logger.warning(
                "Session expired. Starting recovery..."
            )

            recovery_result = self.recovery.recover(url)

            logger.info(recovery_result.message)

            logged_in = self.login.check(
                self.browser.get_page()
            )

            if not logged_in:

                raise RuntimeError(
                    "Unable to establish an authenticated session."
                )

            # Re-read project after recovery
            project = self.loader.platform.read_project()

        # Locate current clip
        clip = self.locator.locate(project)

        # Update session state
        self.state.update(

            logged_in=True,

            project_loaded=True,

            current_clip=clip["clip_number"],

            total_clips=1,

            status="Ready"

        )

        return {

            "project": project,

            "clip": clip,

            "state": self.state,

            "recovery": recovery_result,

            "page": self.browser.get_page()

        }

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def page(self):

        return self.browser.get_page()

    def browser_manager(self):

        return self.browser

    def session_state(self):

        return self.state