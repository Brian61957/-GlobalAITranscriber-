from dataclasses import dataclass, field


@dataclass
class SpeechResult:

    success: bool = False

    transcript: str = ""

    language: str = ""

    provider: str = ""

    error: str = ""

    warnings: list = field(default_factory=list)