from actions.action_locator import ActionLocator
from actions.action_validator import ActionValidator
from actions.action_executor import ActionExecutor


class ActionEngine:

    def __init__(self):

        self.locator = ActionLocator()

        self.validator = ActionValidator()

        self.executor = ActionExecutor()

    # ==================================================
    # Smart Search
    # ==================================================

    def _find_live(self, page, role):

        candidates = []

        # -----------------------------
        # Transcript
        # -----------------------------

        if role == "transcript_box":

            selectors = [

                "textarea",

                'textarea[placeholder]',

                'textarea:not([disabled])',

                '[contenteditable="true"]',

                'input[type="text"]'

            ]

        # -----------------------------
        # Submit
        # -----------------------------

        elif role == "submit_button":

            selectors = [

                'button:has-text("Submit")',

                'button:has-text("Save & Next")',

                'button:has-text("Save and Next")',

                'button:has-text("Save")',

                'button:has-text("Done")',

                'button[type="submit"]',

                '[aria-label*="Submit"]',

                "button"

            ]

        # -----------------------------
        # Start / Good Luck
        # -----------------------------

        elif role == "start_button":

            selectors = [

                'a:has-text("Start Transcribing")',

                'button:has-text("Start Transcribing")',

                'a:has-text("Start Recording")',

                'button:has-text("Start Recording")',

                'a:has-text("Good Luck")',

                'button:has-text("Good Luck")',

                'a:has-text("Start")',

                'button:has-text("Start")',

                'a:has-text("Begin")',

                'button:has-text("Begin")',

                'a:has-text("Continue")',

                'button:has-text("Continue")',

                '[role="button"]:has-text("Start")',

                '[aria-label*="Start"]',

            ]

        # -----------------------------
        # Next
        # -----------------------------

        elif role == "next_button":

            selectors = [

                'button:has-text("Next")',

                '[aria-label*="Next"]',

                "button"

            ]

        # -----------------------------
        # Skip
        # -----------------------------

        elif role == "skip_button":

            selectors = [

                'button:has-text("Skip")',

                '[aria-label*="Skip"]',

                "button"

            ]

        else:

            selectors = []

        for selector in selectors:

            try:

                locator = page.locator(selector)

                count = locator.count()

                for i in range(count):

                    item = locator.nth(i)

                    try:

                        if not item.is_visible():

                            continue

                        if not item.is_enabled():

                            continue

                        candidates.append(item)

                    except Exception:

                        continue

            except Exception:

                continue

        return candidates

    # ==================================================
    # Fill
    # ==================================================

    def fill(

        self,

        page,

        snapshot,

        role,

        text

    ):

        # -----------------------------
        # Snapshot first
        # -----------------------------

        element = self.locator.find(

            snapshot,

            role

        )

        if self.validator.validate(element):

            result = self.executor.fill(

                page,

                element,

                text

            )

            if result.success:

                return result

        # -----------------------------
        # Live search
        # -----------------------------

        live = self._find_live(

            page,

            role

        )

        if not live:

            raise RuntimeError(

                f"No live element found for '{role}'."

            )

        locator = live[0]

        locator.fill(text)

        from actions.action_result import ActionResult

        return ActionResult(

            True,

            "fill",

            "Filled using live locator."

        )

    # ==================================================
    # Click
    # ==================================================

    def click(

        self,

        page,

        snapshot,

        role

    ):

        from utils.logger import logger

        # -----------------------------
        # Snapshot first
        # -----------------------------

        element = self.locator.find(

            snapshot,

            role

        )

        if element:
            logger.info(
                f"[ActionEngine.click] snapshot candidate for '{role}': "
                f"text='{getattr(element, 'text', '')}' "
                f"aria_label='{getattr(element, 'aria_label', '')}' "
                f"selector='{getattr(element, 'selector', '')}'"
            )

        if self.validator.validate(element):

            result = self.executor.click(

                page,

                element

            )

            if result.success:

                self._debug_screenshot(page, role, "snapshot")

                return result

        # -----------------------------
        # Live search
        # -----------------------------

        live = self._find_live(

            page,

            role

        )

        if not live:

            raise RuntimeError(

                f"No live element found for '{role}'."

            )

        locator = live[0]

        try:
            clicked_text = locator.inner_text(timeout=2000).strip()
        except Exception:
            clicked_text = "(could not read text)"

        logger.info(f"[ActionEngine.click] live-search candidate for '{role}': text='{clicked_text}'")

        locator.click()

        self._debug_screenshot(page, role, "live")

        from actions.action_result import ActionResult

        return ActionResult(

            True,

            "click",

            f"Clicked using live locator (text='{clicked_text}')."

        )

    def _debug_screenshot(self, page, role, source):
        from utils.logger import logger
        import os

        try:
            os.makedirs("debug_screenshots", exist_ok=True)
            path = f"debug_screenshots/after_click_{role}_{source}.png"
            page.screenshot(path=path)
            logger.info(f"[ActionEngine.click] Screenshot saved: {path}")
        except Exception as e:
            logger.warning(f"Could not save debug screenshot: {e}")

    # ==================================================
    # Select
    # ==================================================

    def select(

        self,

        page,

        snapshot,

        role,

        value

    ):

        element = self.locator.find(

            snapshot,

            role

        )

        if self.validator.validate(element):

            result = self.executor.select(

                page,

                element,

                value

            )

            if result.success:

                return result

        live = self._find_live(

            page,

            role

        )

        if not live:

            raise RuntimeError(

                f"No live element found for '{role}'."

            )

        locator = live[0]

        locator.select_option(

            label=value

        )

        from actions.action_result import ActionResult

        return ActionResult(

            True,

            "select",

            "Selected using live locator."

        )