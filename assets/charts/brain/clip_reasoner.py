from brain.clip_knowledge import ClipKnowledge
from brain.thought import Thought


class ClipReasoner:

    def analyze(self, clip):

        knowledge = ClipKnowledge()

        knowledge.clip_number = clip.get(
            "clip_number",
            0
        )

        knowledge.has_audio = clip.get(
            "has_audio",
            False
        )

        knowledge.has_draft = clip.get(
            "has_draft",
            False
        )

        knowledge.duration = clip.get(
            "duration",
            ""
        )

        if knowledge.has_audio:

            knowledge.ready = True

            if knowledge.has_draft:

                knowledge.requires_review = True
                knowledge.status = "Review Draft"

            else:

                knowledge.requires_transcription = True
                knowledge.status = "Ready to Transcribe"

        else:

            knowledge.requires_human = True
            knowledge.status = "Missing Audio"

        thought = Thought(

            source="ClipReasoner",

            message=knowledge.status,

            confidence=1.0

        )

        return knowledge, thought