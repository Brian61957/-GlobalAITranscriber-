import random

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from actions.action_result import ActionResult


class ActionExecutor:

    # --------------------------------------------------
    # Internal
    # --------------------------------------------------

    def _locator(self, page, element):

        return page.locator(element.selector)

    # --------------------------------------------------
    # Click
    # --------------------------------------------------

    def click(self, page, element):

        if not element.selector:

            return ActionResult(
                False,
                "click",
                "No selector available."
            )

        try:

            locator = self._locator(page, element)

            locator.wait_for(
                state="visible",
                timeout=5000
            )

            locator.click()

            return ActionResult(
                True,
                "click",
                "Clicked successfully."
            )

        except PlaywrightTimeoutError:

            return ActionResult(
                False,
                "click",
                "Element did not become visible."
            )

        except Exception as e:

            return ActionResult(
                False,
                "click",
                str(e)
            )

    # --------------------------------------------------
    # Human Typing
    # --------------------------------------------------

    def fill(self, page, element, text):

        if not element.selector:

            return ActionResult(
                False,
                "fill",
                "No selector available."
            )

        try:

            locator = self._locator(page, element)

            locator.wait_for(
                state="visible",
                timeout=5000
            )

            locator.click()

            locator.press("Control+a")
            locator.press("Delete")

            # Type humanly: medium speed (60-120ms per character),
            # with natural short pauses at spaces (word boundaries)
            # and slightly longer pauses at punctuation.
            for i, character in enumerate(text):

                if character in (" ", "\n"):
                    delay = random.randint(80, 180)
                elif character in (".", ",", "!", "?", ";", ":"):
                    delay = random.randint(100, 200)
                else:
                    delay = random.randint(60, 120)

                locator.type(
                    character,
                    delay=delay
                )

                # Occasional brief pause mid-sentence (simulates
                # a human pausing to re-read before continuing)
                if i > 0 and i % random.randint(40, 80) == 0:
                    page.wait_for_timeout(random.randint(300, 800))

            return ActionResult(
                True,
                "fill",
                "Human typing completed."
            )

        except PlaywrightTimeoutError:

            return ActionResult(
                False,
                "fill",
                "Element did not become visible."
            )

        except Exception as e:

            return ActionResult(
                False,
                "fill",
                str(e)
            )

    # --------------------------------------------------
    # Select
    # --------------------------------------------------

    def select(self, page, element, value):

        if not element.selector:

            return ActionResult(
                False,
                "select",
                "No selector available."
            )

        try:

            locator = self._locator(page, element)

            locator.wait_for(
                state="visible",
                timeout=5000
            )

            locator.select_option(
                label=value
            )

            return ActionResult(
                True,
                "select",
                "Selection successful."
            )

        except PlaywrightTimeoutError:

            return ActionResult(
                False,
                "select",
                "Element did not become visible."
            )

        except Exception as e:

            return ActionResult(
                False,
                "select",
                str(e)
            )