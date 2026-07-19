from automation.project.project_profile import ProjectProfile


class ProjectMemory:

    def __init__(self):

        self.reset()

    def reset(self):

        self.profile = ProjectProfile()

    def load(self, profile):

        self.profile = profile

    def profile_data(self):

        return self.profile

    def rules(self):

        return {

            "language": self.profile.language,

            "task": self.profile.task_type,

            "translate": self.profile.translate,

            "verbatim": self.profile.verbatim,

            "ignore_fillers": self.profile.ignore_fillers,

            "speaker_labels": self.profile.speaker_labels,

            "timestamps": self.profile.timestamps,

            "british_spelling": self.profile.british_spelling,

            "medical_project": self.profile.medical_project,

            "recording_project": self.profile.recording_project,

            "audio_project": self.profile.audio_project

        }