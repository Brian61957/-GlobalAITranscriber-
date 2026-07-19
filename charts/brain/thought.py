from dataclasses import dataclass
from datetime import datetime


@dataclass
class Thought:

    source: str

    message: str

    confidence: float = 1.0

    timestamp: datetime = datetime.now()