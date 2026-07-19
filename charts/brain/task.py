from dataclasses import dataclass, field


@dataclass
class Task:

    name: str

    description: str = ""

    completed: bool = False