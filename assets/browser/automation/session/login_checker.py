from utils.logger import logger


class LoginChecker:

    def check(self, page):

        logger.info("Checking login status...")

        if page is None:

            logger.warning("No page supplied.")

            return False

        try:

            title = page.title().lower()

            url = page.url.lower()

        except Exception:

            logger.warning("Unable to inspect current page.")

            return False

        # ----------------------------------------
        # Login page detection
        # ----------------------------------------

        if "login" in title:

            logger.warning("Login page detected.")

            return False

        if "/login" in url:

            logger.warning("Login URL detected.")

            return False

        # ----------------------------------------
        # OTP page
        # ----------------------------------------

        if "otp" in title:

            logger.warning("OTP page detected.")

            return False

        # ----------------------------------------
        # Dashboard / transcription page
        # ----------------------------------------

        if "/speech/transcribe/" in url:

            logger.info("User is logged in.")

            return True

        logger.warning("Unable to determine login status.")

        return False