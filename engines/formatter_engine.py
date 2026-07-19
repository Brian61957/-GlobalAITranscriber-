import re


FILLERS = [
    "umm",
    "um",
    "erm",
    "err",
    "uh",
    "ah"
]


BRITISH_SPELLING = {
    "color": "colour",
    "favorite": "favourite",
    "organize": "organise",
    "organizing": "organising",
    "center": "centre",
    "meter": "metre"
}


def remove_fillers(text):

    words = text.split()

    cleaned_words = []

    for word in words:

        word_clean = word.lower().strip(",.!?")

        if word_clean not in FILLERS:
            cleaned_words.append(word)

    return " ".join(cleaned_words)


def apply_british_spelling(text):

    words = text.split()

    output = []

    for word in words:

        key = word.lower()

        if key in BRITISH_SPELLING:
            output.append(BRITISH_SPELLING[key])
        else:
            output.append(word)

    return " ".join(output)


def add_basic_punctuation(text):

    text = text.strip()

    if len(text) == 0:
        return text

    text = text[0].upper() + text[1:]

    if text[-1] not in ".!?":
        text += "."

    return text


def clean_transcript(text, british_spelling=True):

    text = remove_fillers(text)

    if british_spelling:
        text = apply_british_spelling(text)

    text = add_basic_punctuation(text)

    return text