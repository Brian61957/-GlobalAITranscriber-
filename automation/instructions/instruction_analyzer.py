import json
import os

from dotenv import load_dotenv

from utils.logger import logger


class InstructionAnalyzer:
    """
    Reads the raw instruction text captured from the project page and
    fills in a ProjectProfile with a real understanding of the task,
    using an LLM. Falls back to simple keyword rules if no API key is
    configured or the API call fails, so the pipeline never hard-stops.
    """

    SYSTEM_PROMPT = (
        "You are reading task instructions from a transcription or translation "
        "platform. The platform could be anything -- Intron, Appen, Lionbridge, "
        "Remotasks, DataAnnotation, Rev, GoTranscript, or any other. "
        "Extract the rules the worker must follow. "
        "Respond with ONLY a JSON object, no markdown, no commentary:\n"
        "{\n"
        '  "language": string,        // e.g. "English", "French", "" if unclear\n'
        '  "task_type": string,       // "Transcription", "Translation", "Recording", "Review", or other\n'
        '  "is_medical": boolean,\n'
        '  "translate": boolean,      // true only if translation INTO another language is required\n'
        '  "verbatim": boolean,       // keep fillers/false starts exactly as spoken\n'
        '  "ignore_fillers": boolean, // drop um, uh, erm etc.\n'
        '  "speaker_labels": boolean, // label Speaker 1:, Speaker 2: etc.\n'
        '  "timestamps": boolean,\n'
        '  "british_spelling": boolean,\n'
        '  "format_notes": string,    // any specific format rules (e.g. how to handle music, noise, overlapping speech)\n'
        '  "dos": [string],\n'
        '  "donts": [string]\n'
        "}"
    )

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("INSTRUCTION_MODEL", "gpt-4o-mini")

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def analyze(self, profile):
        text = (profile.instructions or "").strip()

        if not text:
            logger.warning("No instruction text to analyze.")
            return profile

        data = self._analyze_with_ai(text)

        if data is None:
            logger.warning(
                "Falling back to keyword-based instruction analysis."
            )
            data = self._analyze_with_rules(text)

        self._apply(profile, data)

        return profile

    # --------------------------------------------------
    # AI Path
    # --------------------------------------------------

    def _analyze_with_ai(self, text):
        if not self.api_key:
            logger.warning(
                "OPENAI_API_KEY not set — skipping AI instruction analysis."
            )
            return None

        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": text[:8000]},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )

            raw = response.choices[0].message.content

            data = json.loads(raw)

            logger.info("AI instruction analysis completed.")

            return data

        except Exception as e:
            logger.warning(f"AI instruction analysis failed: {e}")
            return None

    # --------------------------------------------------
    # Fallback Path (keyword rules)
    # --------------------------------------------------

    def _analyze_with_rules(self, text):
        lower = text.lower()

        # Transcription is checked first -- "transcri" wins over "translat"
        # because instructions commonly say "do not translate, transcribe verbatim"
        if "transcri" in lower:
            task_type = "Transcription"
        elif "record" in lower:
            task_type = "Recording"
        elif "translat" in lower:
            task_type = "Translation"
        else:
            task_type = ""

        # Only set translate=True if the task is genuinely a translation
        # task -- not just because the word "translate" appears in a
        # "do not translate" instruction.
        negated = any(p in lower for p in (
            "do not translat", "don't translat", "dont translat",
            "no translation", "without translat", "not translat",
        ))
        translate = (task_type == "Translation") and not negated

        return {
            "language": "French" if "french" in lower else "",
            "task_type": task_type,
            "is_medical": "medical" in lower or "clinical" in lower,
            "translate": translate,
            "verbatim": "verbatim" in lower,
            "ignore_fillers": "umm" in lower or "erm" in lower or "filler" in lower,
            "speaker_labels": "speaker" in lower,
            "timestamps": "timestamp" in lower,
            "british_spelling": "british" in lower,
            "dos": [],
            "donts": [],
        }

    # --------------------------------------------------
    # Apply results onto the profile
    # --------------------------------------------------

    def _apply(self, profile, data):
        profile.language = data.get("language", "") or profile.language
        profile.task_type = data.get("task_type", "") or profile.task_type
        profile.is_medical = bool(data.get("is_medical", False))
        profile.format_notes = data.get("format_notes", "") or ""
        profile.translate = bool(data.get("translate", False))
        profile.verbatim = bool(data.get("verbatim", False))
        profile.ignore_fillers = bool(data.get("ignore_fillers", False))
        profile.speaker_labels = bool(data.get("speaker_labels", False))
        profile.timestamps = bool(data.get("timestamps", False))
        profile.british_spelling = bool(data.get("british_spelling", False))
        profile.dos = data.get("dos", []) or []
        profile.donts = data.get("donts", []) or []
