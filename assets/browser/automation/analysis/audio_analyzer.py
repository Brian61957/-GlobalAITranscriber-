class AudioAnalyzer:

    def analyze(self, project):

        text = project["text"].lower()

        audio_required = True

        if "skip" in text and "music" in text:

            music_policy = "Skip"

        else:

            music_policy = "Transcribe"

        return {

            "audio_required": audio_required,

            "music_policy": music_policy

        }