import os

from faster_whisper import WhisperModel

from speech.speech_provider import SpeechProvider
from speech.speech_result import SpeechResult

from utils.logger import logger

# All Faster-Whisper model sizes in order of accuracy/size.
# tiny   ~39M params  -- fastest, lowest accuracy
# base   ~74M params  -- good balance for English
# small  ~244M params -- better multilingual
# medium ~769M params -- strong multilingual, good for African languages
# large-v2  ~1.5B    -- near state-of-the-art
# large-v3  ~1.5B    -- best available, strongest on low-resource languages
#                        (Oromo, Swahili, etc.)
VALID_MODELS = ["tiny", "base", "small", "medium", "large-v2", "large-v3"]


class FasterWhisperProvider(SpeechProvider):

    def __init__(self, model_size=None):
        self.model = None

        # Priority: explicit argument > WHISPER_MODEL env var > "base"
        self.model_name = (
            model_size
            or os.getenv("WHISPER_MODEL", "base")
        )

        if self.model_name not in VALID_MODELS:
            logger.warning(
                f"Unknown Faster-Whisper model '{self.model_name}'. "
                f"Falling back to 'base'. Valid options: {VALID_MODELS}"
            )
            self.model_name = "base"

    def name(self):
        return f"Faster-Whisper ({self.model_name})"

    def available(self):
        try:
            if self.model is None:
                logger.info(f"Loading Faster-Whisper model: {self.model_name}")

                # large-v2/v3 benefit from float16 on GPU; we stay on
                # int8 for CPU compatibility across all machines.
                self.model = WhisperModel(
                    self.model_name,
                    device="cpu",
                    compute_type="int8",
                )

            return True

        except Exception as e:
            logger.warning(f"Faster-Whisper unavailable: {e}")
            return False

    def transcribe(
        self,
        audio_file,
        instructions=None,
        language=None,
        translate=False,
        include_timestamps=False,
    ):
        result = SpeechResult()

        try:
            logger.info(f"Transcribing with {self.name()}...")

            segments, info = self.model.transcribe(
                audio_file,
                language=language if language else None,
                task="translate" if translate else "transcribe",
                beam_size=5,
                vad_filter=True,
            )

            segments_list = list(segments)

            transcript = []

            for segment in segments_list:
                text = segment.text.strip()

                if include_timestamps:
                    minutes, seconds = divmod(int(segment.start), 60)
                    text = f"[{minutes:02d}:{seconds:02d}] {text}"

                transcript.append(text)

            result.success = True
            result.provider = self.name()
            result.language = info.language
            result.transcript = (
                "\n".join(transcript) if include_timestamps
                else " ".join(transcript)
            ).strip()
            result._segments = segments_list

            logger.info(f"Transcription completed ({self.model_name}).")
            return result

        except Exception as e:
            logger.exception("Offline transcription failed.")
            result.success = False
            result.provider = self.name()
            result.error = str(e)
            return result
