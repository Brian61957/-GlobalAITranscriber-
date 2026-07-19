from automation.platforms.platform_factory import PlatformFactory
from utils.logger import logger


class ProjectLoader:

    def __init__(self, browser):

        self.browser = browser

        self.platform = PlatformFactory().create(

            "intron",

            browser

        )

    # --------------------------------------------------
    # Open and Read Project
    # --------------------------------------------------

    def load(self, url):

        logger.info("Opening project...")

        self.platform.open_project(url)

        logger.info("Reading project...")

        return self.platform.read_project()

    # --------------------------------------------------
    # Read Current Project
    # --------------------------------------------------

    def read(self):

        logger.info("Reading current project...")

        return self.platform.read_project()

    # --------------------------------------------------
    # Current Platform
    # --------------------------------------------------

    def current_platform(self):

        return self.platform