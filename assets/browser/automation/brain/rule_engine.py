class RuleEngine:

    def parse(self, text):

        text = text.lower()

        rules = {

            "ignore_fillers": False,
            "british_spelling": False,
            "timestamps": False,
            "multiple_speakers": False,
            "translate": False

        }

        if "ignore" in text and "erm" in text:
            rules["ignore_fillers"] = True

        if "british" in text:
            rules["british_spelling"] = True

        if "timestamp" in text:
            rules["timestamps"] = True

        if "multiple speaker" in text:
            rules["multiple_speakers"] = True

        if "translate" in text:
            rules["translate"] = True

        return rules