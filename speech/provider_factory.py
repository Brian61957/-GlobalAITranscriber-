from speech.providers.faster_whisper_provider import FasterWhisperProvider, VALID_MODELS
from speech.providers.openai_provider import OpenAIProvider

# Maps UI dropdown labels to internal provider/model config.
# Adding a new model: just add a new entry here -- everything else
# (SpeechManager, PipelineEngine, UI dropdown) picks it up automatically.
PROVIDER_CONFIGS = {
    # Faster-Whisper local models
    "Faster-Whisper (base)":     {"provider": "faster-whisper", "model_size": "base"},
    "Faster-Whisper (small)":    {"provider": "faster-whisper", "model_size": "small"},
    "Faster-Whisper (medium)":   {"provider": "faster-whisper", "model_size": "medium"},
    "Faster-Whisper (large-v2)": {"provider": "faster-whisper", "model_size": "large-v2"},
    "Faster-Whisper (large-v3)": {"provider": "faster-whisper", "model_size": "large-v3"},
    # OpenAI cloud models
    "GPT-4o Transcribe (OpenAI)": {"provider": "openai", "model_size": None},
}

# The default shown in the UI dropdown
DEFAULT_MODEL = "Faster-Whisper (base)"


class ProviderFactory:

    def create(self, provider_label=DEFAULT_MODEL):
        config = PROVIDER_CONFIGS.get(provider_label)

        if config is None:
            # Fallback: check if the label is a raw Faster-Whisper model
            # size (e.g. "large-v3" passed programmatically)
            if provider_label in VALID_MODELS:
                config = {"provider": "faster-whisper", "model_size": provider_label}
            else:
                raise RuntimeError(
                    f"Unknown model '{provider_label}'. "
                    f"Valid options: {list(PROVIDER_CONFIGS.keys())}"
                )

        if config["provider"] == "faster-whisper":
            provider = FasterWhisperProvider(model_size=config["model_size"])
        elif config["provider"] == "openai":
            provider = OpenAIProvider()
        else:
            raise RuntimeError(f"Unknown provider type: {config['provider']}")

        if not provider.available():
            raise RuntimeError(
                f"'{provider_label}' is not available. "
                "Check dependencies and API keys."
            )

        return provider
