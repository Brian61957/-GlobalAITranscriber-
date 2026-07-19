from automation.platforms.base_platform import BasePlatform

from browser.project_reader import ProjectReader
from browser.page_scanner import PageScanner

from utils.logger import logger


class IntronPlatform(BasePlatform):

    def __init__(self, browser):

        self.browser = browser

        self.page = None

    def open_project(self, url):

        logger.info("Opening project...")

        self.page = self.browser.open_project(url)

        return self.page

    def read_project(self):

        logger.info("Reading project...")

        reader = ProjectReader(self.page)

        scanner = PageScanner(self.page)

        project = reader.read_project()

        project["page"] = scanner.scan()

        return project

    def locate_audio(self):

        logger.info("Locating audio...")

        return []

    def locate_draft(self):

        logger.info("Looking for draft transcript...")

        return None

    def next_clip(self):

        logger.info("Moving to next clip...")

        return False

    def close(self):

        logger.info("Closing browser...")

        self.browser.close()