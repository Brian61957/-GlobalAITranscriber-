from dataclasses import dataclass


@dataclass
class RecoveryResult:

    success: bool = False

    recovered: bool = False

    page_type: str = ""

    message: str = ""