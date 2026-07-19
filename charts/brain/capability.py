from enum import Enum


class Capability(Enum):

    WAIT_FOR_LOGIN = "wait_for_login"

    READ_INSTRUCTIONS = "read_instructions"

    PLAY_AUDIO = "play_audio"

    TRANSCRIBE_AUDIO = "transcribe_audio"

    FILL_TRANSCRIPT = "fill_transcript"

    SUBMIT_TRANSCRIPT = "submit_transcript"

    SKIP_CLIP = "skip_clip"

    NEXT_CLIP = "next_clip"

    OBSERVE = "observe"

    FINISHED = "finished"