from brain.situation_type import SituationType


class ActionPolicy:

    def choose(self, situation):

        # ----------------------------
        # Login page
        # ----------------------------

        if situation.type == SituationType.LOGIN:

            return "wait_for_login"

        # ----------------------------
        # Instructions page
        # ----------------------------

        if situation.type == SituationType.INSTRUCTIONS:

            return "read_instructions"

        # ----------------------------
        # Transcription page
        # ----------------------------

        if situation.type == SituationType.TRANSCRIPTION:

            if situation.can_transcribe:

                return "play_audio"

            if situation.can_submit:

                return "submit_transcript"

        # ----------------------------
        # Fallback
        # ----------------------------

        return "observe"