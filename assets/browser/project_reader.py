from playwright.sync_api import Page


class ProjectReader:

    def __init__(self, page: Page):
        self.page = page

    def get_page_title(self):
        return self.page.title()

    def get_visible_text(self):
        """
        Returns all visible text from the page.
        """
        return self.page.locator("body").inner_text()

    def read_project(self):
        return {
            "title": self.get_page_title(),
            "text": self.get_visible_text()
        }