from brain.situation_type import SituationType


class Situation:

    def __init__(self):

        # ----------------------------
        # High-level situation
        # ----------------------------

        self.type = SituationType.UNKNOWN

        # ----------------------------
        # Authentication
        # ----------------------------

        self.logged_in = False

        # ----------------------------
        # Page readiness
        # ----------------------------

        self.audio_available = False

        self.audio_playing = False

        self.transcript_editor = False

        self.submit_available = False

        self.skip_available = False

        self.instructions_visible = False

        # ----------------------------
        # AI understanding
        # ----------------------------

        self.can_transcribe = False

        self.can_submit = False

        self.requires_login = False

        self.requires_instructions = False

        # ----------------------------
        # Human readable
        # ----------------------------

        self.description = ""