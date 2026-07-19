class DraftAnalyzer:

    def analyze(self, project):

        text = project["text"].lower()

        draft_supported = (
            "draft transcript" in text
        )

        return {

            "draft_supported": draft_supported

        }