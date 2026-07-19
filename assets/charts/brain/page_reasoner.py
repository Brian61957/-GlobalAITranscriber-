from brain.situation import Situation
from brain.situation_type import SituationType


class PageReasoner:

    def analyze(self, snapshot):

        situation = Situation()

        title = (snapshot.title or "").lower()

        url = (snapshot.url or "").lower()

        # ---------------------------------
        # Detect Login
        # ---------------------------------

        if "login" in title or "/login" in url:

            situation.type = SituationType.LOGIN

            situation.requires_login = True

            situation.description = "User must log in."

            return situation

        # ---------------------------------
        # Detect Instructions
        # ---------------------------------

        if "instruction" in url:

            situation.type = SituationType.INSTRUCTIONS

            situation.instructions_visible = True

            situation.requires_instructions = True

            situation.description = "Instruction page detected."

            return situation

        # ---------------------------------
        # Detect Transcription
        # ---------------------------------

        if "/speech/transcribe/" in url:

            situation.type = SituationType.TRANSCRIPTION

            situation.logged_in = True

        # ---------------------------------
        # Analyze available controls
        # ---------------------------------

        for button in snapshot.buttons:

            role = getattr(button, "role", "")

            if role == "play_audio":

                situation.audio_available = True

            elif role == "submit_transcript":

                situation.submit_available = True

            elif role == "skip_clip":

                situation.skip_available = True

        for textbox in snapshot.textboxes:

            if getattr(textbox, "role", "") == "transcript_editor":

                situation.transcript_editor = True

        # ---------------------------------
        # AI capabilities
        # ---------------------------------

        situation.can_transcribe = (

            situation.audio_available

            and situation.transcript_editor

        )

        situation.can_submit = (

            situation.submit_available

        )

        situation.description = (

            f"{situation.type.value} page"

        )

        return situation