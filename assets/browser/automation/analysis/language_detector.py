class LanguageDetector:

    def detect(self, project):

        text = project["text"].lower()

        if "french" in text:
            return "French"

        if "swahili" in text:
            return "Swahili"

        if "english" in text:
            return "English"

        if "arabic" in text:
            return "Arabic"

        return "Unknown"