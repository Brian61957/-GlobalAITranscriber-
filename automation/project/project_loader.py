from automation.project.project_reader import ProjectReader
from automation.project.project_navigator import ProjectNavigator

from utils.logger import logger


class ProjectLoader:

    def __init__(self, browser):

        self.browser = browser

    def load(self, url):

        logger.info("=" * 60)

        logger.info("PROJECT INITIALIZATION")

        logger.info("=" * 60)

        page = self.browser.open_project(url)

        reader = ProjectReader(page)

        profile = reader.read()

        navigator = ProjectNavigator(page)

        task_page = navigator.enter_task()

        return {

            "instruction_page": page,

            "task_page": task_page,

            "profile": profile

        }