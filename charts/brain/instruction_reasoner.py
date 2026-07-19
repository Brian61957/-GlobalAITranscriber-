from brain.instruction_knowledge import InstructionKnowledge
from brain.thought import Thought


class InstructionReasoner:

    def analyze(self, project):

        knowledge = InstructionKnowledge()

        knowledge.language = project.get("language", "Unknown")

        knowledge.medical = project.get("medical", False)

        knowledge.translate = project.get("translate", False)

        knowledge.british_spelling = project.get(
            "british_spelling",
            False
        )

        knowledge.ignore_fillers = project.get(
            "ignore_fillers",
            False
        )

        knowledge.speaker_labels = project.get(
            "multiple_speakers",
            False
        )

        knowledge.timestamps = project.get(
            "speaker_timestamps",
            False
        )

        knowledge.skip_inaudible = project.get(
            "skip_inaudible",
            False
        )

        knowledge.punctuation = project.get(
            "punctuation",
            True
        )

        knowledge.numbers_as_digits = project.get(
            "numbers_as_digits",
            False
        )

        if knowledge.translate:

            knowledge.task = "Translate"

        else:

            knowledge.task = "Transcribe"

        thought = Thought(

            source="InstructionReasoner",

            message=f"{knowledge.task} project detected ({knowledge.language}).",

            confidence=1.0

        )

        return knowledge, thought