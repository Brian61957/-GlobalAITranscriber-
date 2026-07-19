from speech.provider_factory import ProviderFactory, DEFAULT_MODEL
from speech.transcript_reviewer import TranscriptReviewer
from speech.transcript import Transcript

from utils.logger import logger


class SpeechManager:

    def __init__(self, provider_label=DEFAULT_MODEL):

        self.provider = ProviderFactory().create(provider_label)

        self.reviewer = TranscriptReviewer()

        logger.info(f"Speech provider: {self.provider.name()}")

    # --------------------------------------------------
    # Speech -> Transcript
    # --------------------------------------------------

    def transcribe(self, audio_file, instructions=None, language=None, profile=None):
        """
        profile, if given, is the ProjectProfile produced by
        InstructionAnalyzer -- it's what lets the reviewer actually act
        on what was understood (verbatim, ignore_fillers, british_spelling,
        speaker_labels, timestamps), instead of just extracting those rules
        and never using them.
        """

        logger.info("Starting speech transcription...")

        translate = bool(getattr(profile, "translate", False)) if profile else False
        include_timestamps = bool(getattr(profile, "timestamps", False)) if profile else False

        # Sanitize language -- empty string crashes Faster-Whisper;
        # None means "auto-detect" which is the correct fallback.
        safe_language = language if language else None

        result = self.provider.transcribe(
            audio_file=audio_file,
            instructions=instructions,
            language=safe_language,
            translate=translate,
            include_timestamps=include_timestamps,
        )

        if not result.success:
            logger.error(result.error)
            return result

        logger.info("Reviewing transcript...")

        try:
            transcript_obj = Transcript(
                text=result.transcript,
                raw_text=result.transcript,
                language=result.language or "unknown",
                audio_file=audio_file,
            )

            reviewed = self.reviewer.review(transcript_obj, profile)

            if reviewed:
                result.transcript = reviewed.text
                if reviewed.warnings:
                    result.warnings = reviewed.warnings
                    for warning in reviewed.warnings:
                        logger.warning(warning)

        except Exception as e:
            logger.warning(f"Transcript review failed: {e}")

        logger.info("Speech pipeline completed.")

        return result
