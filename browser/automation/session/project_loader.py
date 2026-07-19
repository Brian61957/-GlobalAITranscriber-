from automation.platforms.platform_factory import PlatformFactory
from utils.logger import logger


class ProjectLoader:

    def __init__(self, browser):

        self.platform = PlatformFactory().create(

            "intron",

            browser

        )

    def load(self, url):

        logger.info("Opening project...")

        self.platform.open_project(url)

        logger.info("Reading project...")

        return self.platform.read_project()