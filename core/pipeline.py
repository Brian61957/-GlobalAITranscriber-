def process_audio(audio_path):

    print("STEP 1")

    from engines.audio_engine import transcribe_audio

    print("STEP 2")

    from engines.formatter_engine import clean_transcript

    print("STEP 3")

    from engines.confidence_engine import calculate_confidence

    print("STEP 4")

    audio_result = transcribe_audio(audio_path)

    print("STEP 5")

    transcript = audio_result["transcript"]
    language = audio_result["language"]
    duration = audio_result["duration"]

    formatted = clean_transcript(transcript)

    print("STEP 6")

    confidence = calculate_confidence(
        transcript=formatted,
        language=language,
        duration=duration
    )

    print("STEP 7")

    return {
        "transcript": transcript,
        "translation": transcript,
        "formatted": formatted,
        "language": language,
        "duration": duration,
        "confidence": confidence
    }