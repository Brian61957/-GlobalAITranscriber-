import os

from dotenv import load_dotenv
from openai import OpenAI

from speech.transcript import Transcript
from speech.transcription_result import TranscriptionResult

from utils.logger import logger


class OpenAISpeechClient:

    def __init__(self):

        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:

            raise RuntimeError(
                "OPENAI_API_KEY not found in .env"
            )

        self.client = OpenAI(
            api_key=api_key
        )

    # -------------------------------------------------
    # Speech → Text
    # -------------------------------------------------

    def transcribe(

        self,

        audio_file,

        language=None,

        prompt=None,

        translate=False,

        include_timestamps=False

    ):

        logger.info(
            f"Transcribing {audio_file}"
        )

        try:

            if translate:
                # Only whisper-1 exposes a dedicated translation endpoint
                # (always translates to English).
                with open(audio_file, "rb") as audio:
                    response = self.client.audio.translations.create(
                        model="whisper-1",
                        file=audio,
                        prompt=prompt,
                    )
                text = response.text

            elif include_timestamps:
                # whisper-1's verbose_json gives us per-segment timing;
                # gpt-4o-transcribe doesn't expose segments the same way.
                with open(audio_file, "rb") as audio:
                    response = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio,
                        language=language,
                        prompt=prompt,
                        response_format="verbose_json",
                    )
                lines = []
                for segment in getattr(response, "segments", []) or []:
                    minutes, seconds = divmod(int(segment["start"]), 60)
                    lines.append(f"[{minutes:02d}:{seconds:02d}] {segment['text'].strip()}")
                text = "\n".join(lines) if lines else response.text

            else:
                with open(audio_file, "rb") as audio:
                    response = self.client.audio.transcriptions.create(
                        model="gpt-4o-transcribe",
                        file=audio,
                        language=language,
                        prompt=prompt,
                    )
                text = response.text

            transcript = Transcript(

                text=text,

                raw_text=text,

                language=language or "unknown",

                confidence=1.0,

                audio_file=audio_file

            )

            logger.info(
                "Transcription completed."
            )

            return TranscriptionResult(

                success=True,

                transcript=transcript,

                message="Transcription successful."

            )

        except Exception as error:

            logger.exception(
                "Speech transcription failed."
            )

            return TranscriptionResult(

                success=False,

                transcript=None,

                message=str(error)

            )