from bs4 import BeautifulSoup


def parse_instruction_text(text):

    rules = {
        "language": "Auto",
        "multiple_speakers": False,
        "british_spelling": False,
        "ignore_fillers": False,
        "timestamps": False
    }

    text = text.lower()

    if "multiple speakers" in text:
        rules["multiple_speakers"] = True

    if "british version" in text or "british spelling" in text:
        rules["british_spelling"] = True

    if "umm" in text or "erm" in text or "word fillers" in text:
        rules["ignore_fillers"] = True

    if "timestamp" in text:
        rules["timestamps"] = True

    return rules