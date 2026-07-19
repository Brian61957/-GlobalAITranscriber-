from dataclasses import dataclass


@dataclass
class ActionResult:

    success: bool = False

    action: str = ""

    message: str = ""