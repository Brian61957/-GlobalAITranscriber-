from dataclasses import dataclass, field
from typing import List


@dataclass
class Transcript:

    text: str

    raw_text: str

    language: str = "unknown"

    confidence: float = 1.0

    reviewed: bool = False

    corrections: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)

    audio_file: str = ""