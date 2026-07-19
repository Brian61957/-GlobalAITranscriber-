"""
TaskSubmitter -- platform-agnostic task interaction.

Finds the transcript field, submit button, and next-task trigger
on ANY transcription/translation platform by reasoning about what
each element looks like and what it does, rather than relying on
hardcoded selectors specific to one site.
"""

import random

from browser.page_scanner import PageScanner
from actions.action_engine import ActionEngine
from actions.action_result import ActionResult
from utils.logger import logger


class TaskSubmitter:

    # Phrases on any platform that signal the task queue is empty.
    # Checked case-insensitively against the full page body text.
    NO_MORE_TASKS_TEXT = [
        "no more tasks", "all tasks completed", "no tasks available",
        "queue is empty", "nothing left", "project complete",
        "project completed", "congratulations", "you're all done",
        "you are all done", "all done", "no clips left",
        "no clips remaining", "nothing to transcribe",
        "no audio available", "all caught up",
    ]

    def __init__(self, page):
        self.page = page
        self.engine = ActionEngine()

    def _scan(self):
        return PageScanner(self.page).scan()

    # --------------------------------------------------
    # Fill Transcript -- reason about the field type
    # --------------------------------------------------

    def fill_transcript(self, text):
        """
        Finds the transcript input on ANY platform by trying selectors
        in order of specificity. Types at human speed once found.
        """
        # Try progressively broader selectors -- most platforms use
        # a <textarea>, some use contenteditable divs
        field_selectors = [
            "textarea[placeholder*='verbatim']",
            "textarea[placeholder*='text here']",
            "textarea[placeholder*='transcri']",
            "textarea[placeholder*='translat']",
            "textarea[placeholder*='type']",
            "textarea[placeholder*='enter']",
            "[contenteditable='true']",
            "textarea",
        ]

        locator = None
        matched_selector = None

        for selector in field_selectors:
            try:
                candidate = self.page.locator(selector)
                if candidate.count() > 0:
                    locator = candidate.first
                    matched_selector = selector
                    break
            except Exception:
                continue

        if locator is None:
            # Last resort: ask the smart engine
            snapshot = self._scan()
            result = self.engine.fill(self.page, snapshot, "transcript_box", text)
            logger.info(f"Transcript filled via ActionEngine ({result.message}).")
            return result

        try:
            locator.wait_for(state="visible", timeout=8000)
            locator.click()
            locator.press("Control+a")
            locator.press("Delete")

            logger.info(f"Typing transcript into field ({matched_selector}) at human speed...")

            for i, char in enumerate(text):
                if char in (" ", "\n"):
                    delay = random.randint(80, 180)
                elif char in (".", ",", "!", "?", ";", ":"):
                    delay = random.randint(100, 200)
                else:
                    delay = random.randint(60, 120)

                locator.type(char, delay=delay)

                if i > 0 and i % random.randint(40, 80) == 0:
                    self.page.wait_for_timeout(random.randint(300, 700))

            logger.info("Transcript typed successfully.")
            return ActionResult(True, "fill", "Transcript typed at human speed.")

        except Exception as e:
            logger.warning(f"Human typing failed: {e}")
            return ActionResult(False, "fill", str(e))

    # --------------------------------------------------
    # Submit -- find the right button on any platform
    # --------------------------------------------------

    def submit(self):
        snapshot = self._scan()
        result = self.engine.click(self.page, snapshot, "submit_button")
        logger.info(f"Submit clicked ({result.message}).")

        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            logger.warning("Network idle timeout after submit.")

        return result

    # --------------------------------------------------
    # Next Task -- detect and advance to the next clip
    # --------------------------------------------------

    def has_next_task(self):
        if self._task_is_present():
            return True

        if self._explicitly_no_more_tasks():
            logger.info("No more tasks detected.")
            return False

        # Try clicking whatever advances to the next task
        for role in ("next_button", "skip_button"):
            try:
                snapshot = self._scan()
                self.engine.click(self.page, snapshot, role)
                logger.info(f"Clicked '{role}' to advance.")

                try:
                    self.page.wait_for_load_state("networkidle", timeout=10000)
                except Exception:
                    pass

                if self._task_is_present():
                    return True

            except Exception:
                continue

        if self._explicitly_no_more_tasks():
            logger.info("No more tasks detected.")
        else:
            logger.warning("Could not confirm a next task -- assuming done.")

        return False

    def _task_is_present(self):
        snapshot = self._scan()
        return bool(snapshot.textboxes)

    def _explicitly_no_more_tasks(self):
        try:
            body_text = self.page.locator("body").inner_text().lower()
        except Exception:
            body_text = ""
        return any(phrase in body_text for phrase in self.NO_MORE_TASKS_TEXT)
