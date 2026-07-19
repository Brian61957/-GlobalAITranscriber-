from automation.project.project_profile import ProjectProfile
from automation.instructions.instruction_analyzer import InstructionAnalyzer

from utils.logger import logger


class ProjectReader:

    def __init__(self, page):

        self.page = page

        self.analyzer = InstructionAnalyzer()

    # --------------------------------------------------
    # Safe Helpers
    # --------------------------------------------------

    def _text(self, selector):

        try:

            locator = self.page.locator(selector)

            if locator.count():

                return locator.first.inner_text().strip()

        except Exception:

            pass

        return ""

    def _body(self):

        try:

            return self.page.locator("body").inner_text()

        except Exception:

            return ""

    # --------------------------------------------------
    # Read Project
    # --------------------------------------------------

    def read(self):

        logger.info("=" * 60)
        logger.info("READING PROJECT INSTRUCTIONS")
        logger.info("=" * 60)

        profile = ProjectProfile()

        # Detect platform from URL instead of hardcoding "Intron"
        try:
            from urllib.parse import urlparse
            domain = urlparse(self.page.url).hostname or "unknown"
            profile.platform = domain
        except Exception:
            profile.platform = "unknown"

        profile.title = (
            self._text("h1")
            or self._text("h2")
            or self._text("title")
            or "Untitled Project"
        )

        # Read the full page body as the main instruction text
        full_body = self._body()
        profile.description = full_body
        profile.instructions = full_body

        # Try to read structured instruction sections generically --
        # look for common section IDs and headings used across platforms,
        # not just Intron-specific ones
        section_candidates = [
            # Intron-style anchor IDs
            ("#dos", "#dont", "#howToWork", "#audio", "#paymentInfo"),
            # Generic alternatives
            ("#dos", "#donts", "#how-to", "#audio-example", "#payment"),
            ("#instructions", "#rules", "#guidelines", "#requirements", ""),
        ]

        structured_parts = []

        for dos_id, donts_id, howto_id, audio_id, payment_id in section_candidates:
            dos = self._text(dos_id) if dos_id else ""
            donts = self._text(donts_id) if donts_id else ""
            howto = self._text(howto_id) if howto_id else ""
            audio = self._text(audio_id) if audio_id else ""
            payment = self._text(payment_id) if payment_id else ""

            if dos or donts or howto:
                if dos:
                    structured_parts.append(f"=== DOS ===\n{dos}")
                if donts:
                    structured_parts.append(f"=== DON'TS ===\n{donts}")
                if howto:
                    structured_parts.append(f"=== HOW TO USE ===\n{howto}")
                if audio:
                    structured_parts.append(f"=== AUDIO EXAMPLE ===\n{audio}")
                if payment:
                    structured_parts.append(f"=== PAYMENT ===\n{payment}")
                break

        if structured_parts:
            profile.instructions = full_body + "\n\n" + "\n\n".join(structured_parts)
            logger.info(f"Structured instruction sections captured from {profile.platform}")

        logger.info("Instruction page captured.")

        profile = self.analyzer.analyze(profile)

        logger.info("=" * 60)
        logger.info("PROJECT PROFILE")
        logger.info("=" * 60)

        for key, value in profile.summary().items():

            logger.info(f"{key}: {value}")

        logger.info("=" * 60)

        return profile