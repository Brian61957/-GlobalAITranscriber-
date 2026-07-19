from dataclasses import dataclass


@dataclass
class Decision:

    action: str

    reason: str

    confidence: float = 1.0

    completed: bool = False