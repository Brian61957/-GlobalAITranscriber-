from faster_whisper import WhisperModel

model = None


def load_model():

    global model

    if model is None:

        print("Loading Whisper model...")

        model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8"
        )


def transcribe_audio(audio_path):

    from engines.audio_enhancer import enhance_audio

    audio_path = enhance_audio(audio_path)

    load_model()

    segments, info = model.transcribe(   
        audio_path,
        task="translate",       # Translate everything to English
        beam_size=10,
        language=None,
        vad_filter=True,
        word_timestamps=True
    )

    transcript_parts = []
    segment_data = []

    for segment in segments:

        text = segment.text.strip()

        transcript_parts.append(text)

        segment_data.append(
            {
                "start": segment.start,
                "end": segment.end,
                "text": text
            }
        )

    transcript = " ".join(transcript_parts)

    return {
        "transcript": transcript,
        "language": info.language,
        "duration": info.duration,
        "segments": segment_data
    }
# audio_path = enhance_audio(audio_path)