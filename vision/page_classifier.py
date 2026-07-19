class PageClassifier:

    def classify(self, snapshot):

        title = snapshot.title.lower()

        url = snapshot.url.lower()

        if "/login" in url:
            return "Login"

        if "transcribe" in url:
            return "Transcription"

        if "instruction" in url:
            return "Instructions"

        if "project" in url:
            return "Projects"

        if "dashboard" in url:
            return "Dashboard"

        return "Unknown"