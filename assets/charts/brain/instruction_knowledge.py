from dataclasses import dataclass


@dataclass
class InstructionKnowledge:

    language: str = "Unknown"

    medical: bool = False

    translate: bool = False

    british_spelling: bool = False

    ignore_fillers: bool = False

    speaker_labels: bool = False

    timestamps: bool = False

    punctuation: bool = True

    numbers_as_digits: bool = False

    skip_inaudible: bool = False

    task: str = "Unknown"