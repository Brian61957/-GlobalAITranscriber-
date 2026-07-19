from dataclasses import dataclass
from typing import Optional

from speech.transcript import Transcript


@dataclass
class TranscriptionResult:

    success: bool

    transcript: Optional[Transcript]

    message: str