from brain.decision import Decision
from brain.thought import Thought


class DecisionEngine:

    # =====================================================
    # Situation-Based Decision
    # =====================================================

    def create_policy_decision(self, action):

        descriptions = {

            "wait_for_login":
                "Waiting for the user to authenticate.",

            "read_instructions":
                "Reading project instructions before starting.",

            "play_audio":
                "Start playback to begin transcription.",

            "submit_transcript":
                "Submit the completed transcript.",

            "observe":
                "Continue observing the current page.",

            "finished":
                "Workflow completed."

        }

        reason = descriptions.get(

            action,

            "Situation-based decision."

        )

        thought = Thought(

            source="ActionPolicy",

            message=f"Policy selected '{action}'.",

            confidence=1.0

        )

        decision = Decision(

            action=action,

            reason=reason,

            confidence=1.0

        )

        return decision, thought

    # =====================================================
    # Task-Based Decision
    # =====================================================

    def decide(self, tasks):

        for task in tasks:

            if not task.completed:

                thought = Thought(

                    source="DecisionEngine",

                    message=f"Next planned task: {task.name}",

                    confidence=1.0

                )

                decision = Decision(

                    action=task.name,

                    reason=task.description,

                    confidence=1.0

                )

                return decision, thought

        thought = Thought(

            source="DecisionEngine",

            message="Execution plan completed.",

            confidence=1.0

        )

        decision = Decision(

            action="finished",

            reason="All planned tasks completed.",

            confidence=1.0,

            completed=True

        )

        return decision, thought