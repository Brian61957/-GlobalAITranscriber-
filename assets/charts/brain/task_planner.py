from brain.task import Task
from brain.thought import Thought


class TaskPlanner:

    def create_plan(self, instruction, clip):

        tasks = []

        # --------------------------------
        # Clip not ready
        # --------------------------------

        if clip.requires_human:

            tasks.append(

                Task(
                    name="wait_for_human",
                    description="Human intervention required."
                )

            )

        elif clip.requires_review:

            tasks.extend([

                Task(
                    name="play_audio",
                    description="Play clip audio."
                ),

                Task(
                    name="review_existing_transcript",
                    description="Review existing draft."
                ),

                Task(
                    name="validate_transcript",
                    description="Validate against project instructions."
                ),

                Task(
                    name="wait_for_approval",
                    description="Pause for user approval."
                )

            ])

        elif clip.requires_transcription:

            tasks.extend([

                Task(
                    name="play_audio",
                    description="Play clip audio."
                ),

                Task(
                    name="transcribe_audio",
                    description="Generate transcript."
                ),

                Task(
                    name="validate_transcript",
                    description="Check transcript quality."
                ),

                Task(
                    name="fill_transcript_editor",
                    description="Fill the webpage editor."
                ),

                Task(
                    name="wait_for_approval",
                    description="Pause before submission."
                )

            ])

        # -------------------------------
        # Translation projects
        # -------------------------------

        if instruction.translate:

            tasks.insert(

                2,

                Task(
                    name="translate_transcript",
                    description="Translate transcript."
                )

            )

        thought = Thought(

            source="TaskPlanner",

            message=f"Execution plan created ({len(tasks)} tasks).",

            confidence=1.0

        )

        return tasks, thought