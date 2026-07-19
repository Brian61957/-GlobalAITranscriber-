from browser.browser_manager import BrowserManager
from browser.project_reader import ProjectReader


class Workflow:

    def __init__(self):

        self.browser = BrowserManager()
        self.page = None

    def start(self):

        self.page = self.browser.start()

        print("✓ Browser Started")

    def open_project(self, project_url):

        print("Opening Project...")

        self.page = self.browser.open_project(project_url)

        print("✓ Project Loaded")

    def read_project(self):

        reader = ProjectReader(self.page)

        return reader.read_project()

    def close(self):

        self.browser.close()

        print("✓ Browser Closed")