from browser.project_reader import ProjectReader
from browser.page_scanner import PageScanner


class ProjectIntelligence:

    def __init__(self, page):

        self.page = page

    def analyze(self):

        reader = ProjectReader(self.page)

        scanner = PageScanner(self.page)

        project = reader.read_project()

        scan = scanner.scan()

        return {

            "title": project["title"],

            "text": project["text"],

            "headings": scan["headings"],

            "buttons": scan["buttons"],

            "links": scan["links"]

        }