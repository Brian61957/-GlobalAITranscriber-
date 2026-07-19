import re

from speech.transcript import Transcript

# Common filler words/phrases to strip when a task requires clean
# (non-verbatim) transcripts. Word-boundary matched, case-insensitive.
FILLER_PATTERNS = [
    r"\bum+\b", r"\buh+\b", r"\berm+\b", r"\buhh+\b",
    r"\byou know\b", r"\bi mean\b", r"\bsort of\b", r"\bkind of\b",
    r"\blike,\b",
]

# A modest American -> British spelling map. Not exhaustive, but covers
# the common cases that actually show up in transcription tasks.
BRITISH_SPELLING_MAP = {
    "color": "colour", "colors": "colours", "favorite": "favourite",
    "favorites": "favourites", "organize": "organise", "organized": "organised",
    "organizing": "organising", "organization": "organisation",
    "realize": "realise", "realized": "realised", "center": "centre",
    "centers": "centres", "defense": "defence", "theater": "theatre",
    "traveled": "travelled", "traveling": "travelling", "canceled": "cancelled",
    "cancelling": "cancelling", "apologize": "apologise", "recognize": "recognise",
    "analyze": "analyse", "behavior": "behaviour", "labor": "labour",
    "neighbor": "neighbour", "program": "programme",
}


class TranscriptReviewer:

    def review(self, transcript: Transcript, profile=None):

        text = transcript.text.strip()

        # ------------------------------------------------------
        # Basic cleanup (always applied)
        # ------------------------------------------------------

        while "  " in text:
            text = text.replace("  ", " ")

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = "\n".join(lines)

        # ------------------------------------------------------
        # Apply the rules understood from the instructions
        # ------------------------------------------------------

        verbatim = bool(getattr(profile, "verbatim", False)) if profile else False
        ignore_fillers = bool(getattr(profile, "ignore_fillers", False)) if profile else False
        british_spelling = bool(getattr(profile, "british_spelling", False)) if profile else False
        speaker_labels = bool(getattr(profile, "speaker_labels", False)) if profile else False
        timestamps = bool(getattr(profile, "timestamps", False)) if profile else False

        if ignore_fillers and not verbatim:
            for pattern in FILLER_PATTERNS:
                text = re.sub(pattern, "", text, flags=re.IGNORECASE)
            while "  " in text:
                text = text.replace("  ", " ")
            text = re.sub(r"\s+([,.!?])", r"\1", text)
            transcript.corrections.append("Filler words removed (ignore_fillers rule).")

        if british_spelling:
            def _replace(match):
                word = match.group(0)
                lower = word.lower()
                if lower in BRITISH_SPELLING_MAP:
                    replacement = BRITISH_SPELLING_MAP[lower]
                    if word[0].isupper():
                        replacement = replacement.capitalize()
                    return replacement
                return word

            pattern = r"\b(" + "|".join(re.escape(w) for w in BRITISH_SPELLING_MAP) + r")\b"
            text = re.sub(pattern, _replace, text, flags=re.IGNORECASE)
            transcript.corrections.append("Converted to British spelling.")

        # Final punctuation cleanup
        text = text.strip()
        if text and text[-1].isalnum():
            text += "."

        transcript.text = text
        transcript.reviewed = True

        # ------------------------------------------------------
        # Be honest about rules we can't actually fulfill yet
        # ------------------------------------------------------

        if speaker_labels:
            segments = getattr(transcript, "_segments", None)
            if segments:
                from speech.speaker_labeler import SpeakerLabeler
                labeled = SpeakerLabeler().label(segments, include_timestamps=timestamps)
                if labeled:
                    text = "\n".join(labeled)
                    transcript.text = text
                    transcript.corrections.append("Speaker labels applied (gap-based segmentation).")
            else:
                transcript.warnings.append(
                    "Speaker labels requested but segment data unavailable."
                )

        if timestamps and "[" not in text:
            transcript.warnings.append(
                "Instructions ask for timestamps, but they weren't generated "
                "for this transcription (check the timestamps setting was on "
                "before transcribing)."
            )

        return transcript
