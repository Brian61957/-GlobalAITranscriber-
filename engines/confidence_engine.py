def calculate_confidence(
        transcript,
        language="unknown",
        duration=0
):

    score = 100

    warnings = []

    if len(transcript.strip()) < 10:
        score -= 25
        warnings.append("Transcript is very short.")

    if duration > 0:

        words = len(transcript.split())

        words_per_second = words / duration

        if words_per_second < 1:
            score -= 15
            warnings.append("Very few words for audio duration.")

        elif words_per_second > 5:
            score -= 10
            warnings.append("High speech density detected.")

    if language == "unknown":
        score -= 10
        warnings.append("Language could not be confidently detected.")

    score = max(0, min(score, 100))

    return {
        "confidence": score,
        "warnings": warnings
    }