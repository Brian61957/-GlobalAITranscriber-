from dataclasses import dataclass


@dataclass
class BrainState:

    status: str = "Idle"

    goal: str = ""

    confidence: float = 0.0

    current_step: str = ""

    completed_steps: int = 0

    total_steps: int = 0

    requires_human: bool = False

    last_decision: str = ""