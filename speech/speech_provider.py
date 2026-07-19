from abc import ABC, abstractmethod


class SpeechProvider(ABC):

    @abstractmethod
    def transcribe(
        self,
        audio_file,
        instructions=None,
        language=None,
        translate=False,
        include_timestamps=False
    ):
        """
        Transcribe an audio file.

        Returns:
            SpeechResult
        """
        pass

    @abstractmethod
    def available(self):
        """
        Returns True if this provider can be used.
        """
        pass

    @abstractmethod
    def name(self):
        """
        Returns provider name.
        """
        pass