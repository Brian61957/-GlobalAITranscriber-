def read_project(self):

    logger.info("Reading project...")

    if self.page is None:

        self.page = self.browser.get_page()

    reader = ProjectReader(self.page)

    scanner = PageScanner(self.page)

    project = reader.read_project()

    project["page"] = scanner.scan()

    return project