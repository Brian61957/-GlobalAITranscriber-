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

        self.browser.start()

        self.browser.open_project(url)

        recovery_result = self.recovery.recover(url)

        if not recovery_result.success:

            raise RuntimeError(recovery_result.message)

        logger.info("Authenticated session confirmed.")

        project = self.loader.read()

        clip = self.locator.locate(project)

        total_clips = 1

        if isinstance(project, dict):

            total_clips = project.get("total_clips", 1)

        self.state.update(

            logged_in=True,

            project_loaded=True,

            current_clip=clip["clip_number"],

            total_clips=total_clips,

            status="Ready"

        )

        logger.info("Session ready.")

        return {

            "browser": self.browser,

            "page": self.browser.get_page(),

            "project": project,

            "clip": clip,

            "state": self.state,

            "recovery": recovery_result

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