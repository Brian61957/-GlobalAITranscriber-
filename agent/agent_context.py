from dataclasses import dataclass, field

from brain.brain import Brain


@dataclass
class AgentContext:

    brain: Brain = field(default_factory=Brain)

    project: dict = field(default_factory=dict)

    clip: dict = field(default_factory=dict)

    metadata: dict = field(default_factory=dict)