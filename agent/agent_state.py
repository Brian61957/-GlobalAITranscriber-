from dataclasses import dataclass


@dataclass
class AgentState:

    running: bool = False

    paused: bool = False

    stopped: bool = False

    current_cycle: int = 0

    current_action: str = ""

    completed_actions: int = 0

    failed_actions: int = 0

    last_result: str = ""

    status: str = "Idle"