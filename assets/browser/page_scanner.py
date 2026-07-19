from playwright.sync_api import Page


class PageScanner:

    def __init__(self, page: Page):

        self.page = page

    def scan(self):

        body = self.page.locator("body")

        text = body.inner_text()

        headings = []

        for tag in ["h1", "h2", "h3", "h4"]:

            for element in self.page.locator(tag).all():

                value = element.inner_text().strip()

                if value:

                    headings.append(value)

        buttons = []

        for element in self.page.locator("button").all():

            value = element.inner_text().strip()

            if value:

                buttons.append(value)

        links = []

        for element in self.page.locator("a").all():

            label = element.inner_text().strip()

            href = element.get_attribute("href")

            if href:

                links.append({
                    "text": label,
                    "href": href
                })

        return {

            "text": text,

            "headings": headings,

            "buttons": buttons,

            "links": links

        }