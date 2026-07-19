from dataclasses import dataclass


@dataclass
class CycleResult:

    cycle: int

    action: str

    success: bool

    continue_execution: bool

    message: str

    confidence: float = 1.0