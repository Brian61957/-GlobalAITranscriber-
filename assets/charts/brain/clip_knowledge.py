from dataclasses import dataclass


@dataclass
class ClipKnowledge:

    clip_number: int = 0

    has_audio: bool = False

    has_draft: bool = False

    duration: str = ""

    ready: bool = False

    requires_transcription: bool = False

    requires_review: bool = False

    requires_human: bool = False

    status: str = "Unknown"