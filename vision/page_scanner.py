from vision.page_snapshot import PageSnapshot
from vision.page_element import PageElement
from vision.dom_inspector import DOMInspector


class PageScanner:

    def __init__(self):

        self.inspector = DOMInspector()

    def _create_element(self, locator, element_type, selector):

        meta = self.inspector.inspect(locator)

        return PageElement(

            element_type=element_type,

            text=meta["text"],

            selector=selector,

            visible=meta["visible"],

            enabled=meta["enabled"],

            value=meta["value"],

            placeholder=meta["placeholder"],

            aria_label=meta["aria_label"],

            title=meta["title"],

            element_id=meta["element_id"],

            classes=meta["classes"],

            name=meta["name"],

            data_testid=meta["data_testid"]

        )

    def scan(self, page):

        snapshot = PageSnapshot()

        snapshot.title = page.title()
        snapshot.url = page.url

        # =====================================================
        # HEADINGS
        # =====================================================

        headings = page.locator("h1, h2, h3")

        for i in range(headings.count()):

            try:

                text = headings.nth(i).inner_text().strip()

                if text:
                    snapshot.headings.append(text)

            except Exception:
                pass

        # =====================================================
        # BUTTONS
        # Native buttons
        # =====================================================

        seen = set()

        buttons = page.locator("button")

        for i in range(buttons.count()):

            locator = buttons.nth(i)

            element = self._create_element(

                locator,

                "button",

                f"button >> nth={i}"

            )

            key = (
                element.text,
                element.aria_label,
                element.selector
            )

            if key not in seen:

                snapshot.buttons.append(element)

                seen.add(key)

        # =====================================================
        # CUSTOM BUTTONS
        # div/span with role=button
        # =====================================================

        custom_buttons = page.locator(

            "[role='button']"

        )

        for i in range(custom_buttons.count()):

            locator = custom_buttons.nth(i)

            element = self._create_element(

                locator,

                "button",

                f"[role='button'] >> nth={i}"

            )

            key = (
                element.text,
                element.aria_label,
                element.selector
            )

            if key not in seen:

                snapshot.buttons.append(element)

                seen.add(key)

        # =====================================================
        # TEXT EDITORS
        # textarea
        # =====================================================

        textareas = page.locator("textarea")

        for i in range(textareas.count()):

            locator = textareas.nth(i)

            snapshot.textboxes.append(

                self._create_element(

                    locator,

                    "textarea",

                    f"textarea >> nth={i}"

                )

            )

        # =====================================================
        # CONTENTEDITABLE
        # Future-proof for modern editors
        # =====================================================

        editors = page.locator("[contenteditable='true']")

        for i in range(editors.count()):

            locator = editors.nth(i)

            snapshot.textboxes.append(

                self._create_element(

                    locator,

                    "contenteditable",

                    f"[contenteditable='true'] >> nth={i}"

                )

            )

        # =====================================================
        # DROPDOWNS
        # =====================================================

        dropdowns = page.locator("select")

        for i in range(dropdowns.count()):

            locator = dropdowns.nth(i)

            snapshot.dropdowns.append(

                self._create_element(

                    locator,

                    "select",

                    f"select >> nth={i}"

                )

            )

        # =====================================================
        # AUDIO TAGS
        # =====================================================

        audio = page.locator("audio")

        for i in range(audio.count()):

            locator = audio.nth(i)

            snapshot.audio_players.append(

                self._create_element(

                    locator,

                    "audio",

                    f"audio >> nth={i}"

                )

            )

        # =====================================================
        # SEMANTIC AUDIO CONTROLS
        # Detect play/listen buttons
        # =====================================================

        interactive = page.locator(

            "button, [role='button'], div, span"

        )

        keywords = [

            "play",

            "listen",

            "audio",

            "recording"

        ]

        for i in range(interactive.count()):

            locator = interactive.nth(i)

            try:

                element = self._create_element(

                    locator,

                    "button",

                    f"interactive >> nth={i}"

                )

                searchable = " ".join([

                    element.text,

                    element.aria_label,

                    element.title,

                    element.classes,

                    element.name

                ]).lower()

                if any(

                    word in searchable

                    for word in keywords

                ):

                    key = (

                        element.text,

                        element.aria_label,

                        element.selector

                    )

                    if key not in seen:

                        snapshot.buttons.append(element)

                        seen.add(key)

            except Exception:

                pass

        return snapshot