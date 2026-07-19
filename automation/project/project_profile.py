from dataclasses import dataclass, field


@dataclass
class ProjectProfile:
    # Basic Information
    title: str = ""
    description: str = ""
    platform: str = ""

    # Instructions
    instructions: str = ""
    dos: list = field(default_factory=list)
    donts: list = field(default_factory=list)

    # AI Rules
    language: str = ""
    task_type: str = ""
    translate: bool = False
    verbatim: bool = False
    ignore_fillers: bool = False
    speaker_labels: bool = False
    timestamps: bool = False
    british_spelling: bool = False
    is_medical: bool = False
    format_notes: str = ""

    # Navigation
    start_button = None
    submit_button = None
    next_button = None

    # Runtime
    current_clip = 0
    total_clips = 0

    def summary(self):

        return {

            "title": self.title,

            "platform": self.platform,

            "language": self.language,

            "task_type": self.task_type,

            "translate": self.translate,

            "verbatim": self.verbatim,

            "ignore_fillers": self.ignore_fillers,

            "speaker_labels": self.speaker_labels,

            "timestamps": self.timestamps,

            "british_spelling": self.british_spelling,

            "is_medical": self.is_medical,

            "format_notes": self.format_notes,

        }