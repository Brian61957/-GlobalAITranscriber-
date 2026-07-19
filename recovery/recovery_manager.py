from recovery.recovery_result import RecoveryResult

from browser.login_monitor import LoginMonitor
from observer.page_observer import PageObserver

from utils.logger import logger


class RecoveryManager:

    def __init__(self, browser):

        self.browser = browser

        self.monitor = LoginMonitor()

        self.observer = PageObserver()

    # --------------------------------------------------
    # Recover Session
    # --------------------------------------------------

    def recover(self, project_url):

        page = self.browser.get_page()

        if page is None:

            return RecoveryResult(

                success=False,

                recovered=False,

                page_type="Unknown",

                message="Browser has no active page."

            )

        logger.info("Checking current page...")

        observation = self.observer.observe(page)

        # --------------------------------------------------
        # Already authenticated
        # --------------------------------------------------

        if observation.page_type == "Transcription":

            logger.info("Authenticated session detected.")

            return RecoveryResult(

                success=True,

                recovered=False,

                page_type="Transcription",

                message="Session already valid."

            )

        # --------------------------------------------------
        # Instructions page
        # --------------------------------------------------

        if observation.page_type == "Instructions":

            logger.info("Instructions page detected.")

            return RecoveryResult(

                success=True,

                recovered=False,

                page_type="Instructions",

                message="Instructions page detected."

            )

        # --------------------------------------------------
        # Login Required
        # --------------------------------------------------

        if observation.page_type == "Login":

            logger.warning("Authentication required.")

            print(
                "\n"
                "==================================================\n"
                "Authentication Required\n"
                "==================================================\n\n"
                "Your Intron session has expired or you are not\n"
                "logged in.\n\n"
                "Please sign in using the opened browser window.\n\n"
                "The AI is waiting and will automatically continue\n"
                "after a successful login.\n"
            )

            # Wait until login succeeds
            self.monitor.wait_for_login(page)

            logger.info("Login detected.")

            # Save the new authenticated session
            self.browser.save_session()

            logger.info("Re-opening project...")

            self.browser.open_project(project_url)

            page = self.browser.get_page()

            logger.info("Waiting for transcription page...")

            observation = None

            for _ in range(15):

                page.wait_for_timeout(1000)

                observation = self.observer.observe(page)

                if observation.page_type == "Transcription":

                    logger.info("Transcription page reached.")

                    return RecoveryResult(

                        success=True,

                        recovered=True,

                        page_type="Transcription",

                        message="Session recovered successfully."

                    )

            return RecoveryResult(

                success=False,

                recovered=True,

                page_type=observation.page_type if observation else "Unknown",

                message="Login succeeded but the transcription page was not reached."

            )

        # --------------------------------------------------
        # Unknown Page
        # --------------------------------------------------

        logger.warning(f"Unknown page detected: {observation.page_type}")

        return RecoveryResult(

            success=False,

            recovered=False,

            page_type=observation.page_type,

            message=f"Unknown page type: {observation.page_type}"

        )