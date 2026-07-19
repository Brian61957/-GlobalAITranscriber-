from utils.logger import logger
from browser.auth_manager import AuthManager


class LoginMonitor:

    def __init__(self):

        self.auth = AuthManager()

    def wait_for_login(self, page):

        logger.info("Waiting for user to log in...")

        print("\n" + "=" * 60)
        print("LOGIN REQUIRED")
        print("=" * 60)
        print("1. Log into your Intron account in the browser.")
        print("2. Wait until you can see your projects.")
        print("3. Return to this terminal.")
        input("\nPress ENTER after login is complete...")

        logger.info("Saving browser session...")

        page.context.storage_state(
            path=self.auth.session_path()
        )

        logger.info("Session saved successfully.")