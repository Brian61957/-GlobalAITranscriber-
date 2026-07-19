import os

from dotenv import load_dotenv

from speech.openai_speech_client import OpenAISpeechClient
from speech.speech_result import SpeechResult
from utils.logger import logger


class OpenAIProvider:
    """
    Wraps OpenAISpeechClient so it matches the same interface as
    FasterWhisperProvider: name(), available(), and transcribe(audio_file,
    instructions=None, language=None) -> SpeechResult.
    """

    def name(self):
        return "openai-gpt-4o-transcribe"

    def available(self):
        load_dotenv()
        return bool(os.getenv("OPENAI_API_KEY"))

    def transcribe(self, audio_file, instructions=None, language=None, translate=False, include_timestamps=False):
        if not self.available():
            return SpeechResult(
                success=False,
                transcript="",
                language=language or "unknown",
                provider=self.name(),
                error="OPENAI_API_KEY not set.",
            )

        try:
            client = OpenAISpeechClient()

            result = client.transcribe(
                audio_file=audio_file,
                language=language,
                prompt=instructions,
                translate=translate,
                include_timestamps=include_timestamps,
            )

            if not result.success:
                return SpeechResult(
                    success=False,
                    transcript="",
                    language=language or "unknown",
                    provider=self.name(),
                    error=result.message,
                )

            return SpeechResult(
                success=True,
                transcript=result.transcript.text,
                language=language or "unknown",
                provider=self.name(),
                error="",
            )

        except Exception as e:
            logger.exception("OpenAI transcription failed.")
            return SpeechResult(
                success=False,
                transcript="",
                language=language or "unknown",
                provider=self.name(),
                error=str(e),
            )
