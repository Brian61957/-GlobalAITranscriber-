import librosa
import noisereduce as nr
import soundfile as sf


def enhance_audio(input_path):

    # Load audio
    y, sr = librosa.load(input_path, sr=None)

    # Remove background noise
    reduced_noise = nr.reduce_noise(
        y=y,
        sr=sr
    )

    # Normalize volume
    reduced_noise = reduced_noise / max(abs(reduced_noise))

    output_path = "enhanced_audio.wav"

    sf.write(
        output_path,
        reduced_noise,
        sr
    )

    return output_path