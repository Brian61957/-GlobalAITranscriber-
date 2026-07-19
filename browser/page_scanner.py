from playwright.sync_api import Page

from models.page_snapshot import PageSnapshot
from models.page_element import PageElement


class PageScanner:

    def __init__(self, page: Page):

        self.page = page

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _safe(self, func, default=""):

        try:
            return func()
        except Exception:
            return default

    def _visible(self, locator):

        try:
            return locator.is_visible()
        except Exception:
            return False

    def _enabled(self, locator):

        try:
            return locator.is_enabled()
        except Exception:
            return False

    # --------------------------------------------------
    # Scan
    # --------------------------------------------------

    def scan(self):

        print("=" * 60)
        print("PAGE OBJECT:", self.page)
        print("=" * 60)

        snapshot = PageSnapshot()

        snapshot.title = self._safe(
            lambda: self.page.title()
        )

        snapshot.url = self.page.url

        snapshot.text = self._safe(
            lambda: self.page.locator("body").inner_text()
        )

        # ------------------------------------------
        # Buttons AND styled links (many platforms
        # render action buttons as <a> tags -- the
        # scanner previously ignored these entirely,
        # which is why "Start Transcribing" was never
        # found despite being clearly on the page)
        # ------------------------------------------

        button_locator = self.page.locator("button, a[href], a[role='button']")

        for i in range(button_locator.count()):

            locator = button_locator.nth(i)

            tag = self._safe(lambda: locator.evaluate("el => el.tagName.toLowerCase()"))

            text = self._safe(
                lambda: locator.inner_text()
            ).strip()

            aria = self._safe(
                lambda: locator.get_attribute("aria-label")
            ) or ""

            title = self._safe(
                lambda: locator.get_attribute("title")
            ) or ""

            href = self._safe(
                lambda: locator.get_attribute("href")
            ) or ""

            role = "button"

            label = f"{text} {aria} {title}".lower()

            if "submit" in label:

                role = "submit_button"

            elif any(keyword in label for keyword in ("start transcrib", "good luck", "start recording")):

                role = "start_button"

            elif any(keyword in label for keyword in ("start", "begin", "proceed", "continue")):

                # Only tag generic "start/continue" if it's a real button
                # not a navigation link (nav links usually have long href paths)
                if tag == "button" or not href or href.startswith("#"):

                    role = "start_button"

            elif "play" in label:

                role = "play_button"

            elif "next" in label:

                role = "next_button"

            elif "skip" in label:

                role = "skip_button"

            snapshot.buttons.append(

                PageElement(

                    role=role,

                    tag=tag or "button",

                    selector=f"button, a[href], a[role='button'] >> nth={i}",

                    text=text,

                    visible=self._visible(locator),

                    enabled=self._enabled(locator),

                    aria_label=aria,

                    title=title,

                    href=href,

                )

            )

        # ------------------------------------------
        # Textareas
        # ------------------------------------------

        areas = self.page.locator("textarea")

        for i in range(areas.count()):

            locator = areas.nth(i)

            snapshot.textboxes.append(

                PageElement(

                    role="transcript_box",

                    tag="textarea",

                    selector=f"textarea >> nth={i}",

                    text=self._safe(

                        lambda: locator.input_value()

                    ),

                    visible=self._visible(locator),

                    enabled=self._enabled(locator),

                    placeholder=self._safe(

                        lambda: locator.get_attribute("placeholder")

                    ) or ""

                )

            )

        # ------------------------------------------
        # Inputs
        # ------------------------------------------

        inputs = self.page.locator("input")

        for i in range(inputs.count()):

            locator = inputs.nth(i)

            input_type = (

                self._safe(

                    lambda: locator.get_attribute("type")

                ) or "text"

            ).lower()

            role = "textbox"

            if input_type == "checkbox":

                snapshot.checkboxes.append(

                    PageElement(

                        role="checkbox",

                        tag="input",

                        selector=f'input[type="checkbox"] >> nth={i}',

                        visible=self._visible(locator),

                        enabled=self._enabled(locator)

                    )

                )

                continue

            if input_type == "radio":

                snapshot.radio_buttons.append(

                    PageElement(

                        role="radio",

                        tag="input",

                        selector=f'input[type="radio"] >> nth={i}',

                        visible=self._visible(locator),

                        enabled=self._enabled(locator)

                    )

                )

                continue

            snapshot.textboxes.append(

                PageElement(

                    role=role,

                    tag="input",

                    selector=f"input >> nth={i}",

                    visible=self._visible(locator),

                    enabled=self._enabled(locator),

                    placeholder=self._safe(

                        lambda: locator.get_attribute("placeholder")

                    ) or ""

                )

            )

        # ------------------------------------------
        # Selects
        # ------------------------------------------

        selects = self.page.locator("select")

        for i in range(selects.count()):

            locator = selects.nth(i)

            snapshot.dropdowns.append(

                PageElement(

                    role="dropdown",

                    tag="select",

                    selector=f"select >> nth={i}",

                    visible=self._visible(locator),

                    enabled=self._enabled(locator)

                )

            )

        # ------------------------------------------
        # Audio
        # ------------------------------------------

        audio = self.page.locator("audio")

        for i in range(audio.count()):

            snapshot.audio_players.append(

                PageElement(

                    role="audio_player",

                    tag="audio",

                    selector=f"audio >> nth={i}",

                    visible=True,

                    enabled=True

                )

            )

        # ------------------------------------------
        # Links
        # ------------------------------------------

        links = self.page.locator("a")

        for i in range(links.count()):

            locator = links.nth(i)

            snapshot.links.append(

                PageElement(

                    role="link",

                    tag="a",

                    selector=f"a >> nth={i}",

                    text=self._safe(

                        lambda: locator.inner_text()

                    ),

                    href=self._safe(

                        lambda: locator.get_attribute("href")

                    ) or "",

                    visible=self._visible(locator),

                    enabled=self._enabled(locator)

                )

            )

        # ------------------------------------------
        # Headings
        # ------------------------------------------

        for tag in ["h1", "h2", "h3", "h4"]:

            elements = self.page.locator(tag)

            for i in range(elements.count()):

                locator = elements.nth(i)

                snapshot.headings.append(

                    PageElement(

                        role="heading",

                        tag=tag,

                        selector=f"{tag} >> nth={i}",

                        text=self._safe(

                            lambda: locator.inner_text()

                        ),

                        visible=self._visible(locator),

                        enabled=True

                    )

                )

        return snapshot