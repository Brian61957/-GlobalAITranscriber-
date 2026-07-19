from playwright.sync_api import TimeoutError

from utils.logger import logger


class AudioExtractor:

    def __init__(self, browser):

        self.browser = browser

    # ==================================================
    # Extract Audio URL
    # ==================================================

    def extract(self, page):

        logger.info("Preparing audio extraction...")

        # --------------------------------------------------
        # Strategy 1
        # Already captured?
        # --------------------------------------------------

        existing = self.browser.get_latest_media_url()

        if existing:

            logger.info("Using previously captured audio URL.")

            return existing

        logger.info("No captured audio found.")

        logger.info("Searching for Play button...")

        play_selectors = [

            'button[aria-label*="Play"]',
            'button[title*="Play"]',
            '[data-testid*="play"]',
            'button'

        ]

        clicked = False

        # --------------------------------------------------
        # Strategy 2
        # Click Play
        # --------------------------------------------------

        for selector in play_selectors:

            try:

                buttons = page.locator(selector)

                count = buttons.count()

                for i in range(count):

                    button = buttons.nth(i)

                    if not button.is_visible():

                        continue

                    try:

                        button.scroll_into_view_if_needed()

                    except Exception:

                        pass

                    logger.info(
                        f"Trying Play selector: {selector} ({i})"
                    )

                    button.click(timeout=2000)

                    clicked = True

                    break

                if clicked:

                    break

            except Exception:

                continue

        if clicked:

            logger.info("Waiting for media request...")

            try:

                return self.browser.wait_for_media_request(
                    timeout=10
                )

            except TimeoutError:

                logger.warning(
                    "Play produced no media request."
                )

        # --------------------------------------------------
        # Strategy 3
        # HTML Audio Element
        # --------------------------------------------------

        logger.info(
            "Searching HTML audio elements..."
        )

        try:

            audio = page.locator("audio").first

            if audio.count() > 0:

                src = audio.get_attribute("src")

                if src:

                    logger.info(
                        "Audio element source found."
                    )

                    return src

        except Exception:

            pass

        # --------------------------------------------------
        # Strategy 4
        # Browser cache
        # --------------------------------------------------

        logger.info(
            "Checking captured media requests..."
        )

        requests = self.browser.get_media_requests()

        if requests:

            logger.info(
                "Using most recent captured media."
            )

            return requests[-1]

        # --------------------------------------------------
        # Failure
        # --------------------------------------------------

        raise RuntimeError(

            "Unable to locate the audio source."

        )