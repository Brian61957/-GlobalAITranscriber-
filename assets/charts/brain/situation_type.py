from enum import Enum


class SituationType(Enum):

    UNKNOWN = "Unknown"

    LOGIN = "Login"

    INSTRUCTIONS = "Instructions"

    TRANSCRIPTION = "Transcription"

    LOADING = "Loading"

    ERROR = "Error"

    FINISHED = "Finished"