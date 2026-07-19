from automation.platforms.base_platform import BasePlatform

from browser.project_reader import ProjectReader
from browser.page_scanner import PageScanner

from utils.logger import logger


class IntronPlatform(BasePlatform):

    def __init__(self, browser):

        self.browser = browser

    # --------------------------------------------------
    # Open Project
    # --------------------------------------------------

    def open_project(self, url):

        logger.info("Opening project...")

        return self.browser.open_project(url)

    # --------------------------------------------------
    # Read Project
    # --------------------------------------------------

    def read_project(self):

        logger.info("Reading project...")

        page = self.browser.get_page()

        if page is None:

            raise RuntimeError(
                "Browser has no active page."
            )

        reader = ProjectReader(page)

        scanner = PageScanner(page)

        project = reader.read_project()

        project["page"] = scanner.scan()

        return project

    # --------------------------------------------------
    # Audio
    # --------------------------------------------------

    def locate_audio(self):

        logger.info("Locating audio...")

        return []

    # --------------------------------------------------
    # Draft
    # --------------------------------------------------

    def locate_draft(self):

        logger.info("Looking for draft transcript...")

        return None

    # --------------------------------------------------
    # Next Clip
    # --------------------------------------------------

    def next_clip(self):

        logger.info("Moving to next clip...")

        return False

    # --------------------------------------------------
    # Close
    # --------------------------------------------------

    def close(self):

        logger.info("Closing browser...")

        self.browser.close()