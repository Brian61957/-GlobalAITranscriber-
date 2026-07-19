from audio.audio_extractor import AudioExtractor
from audio.audio_downloader import AudioDownloader


class AudioManager:

    def __init__(self, browser):

        self.browser = browser

        self.extractor = AudioExtractor(browser)

        self.downloader = AudioDownloader()

    # -----------------------------------------
    # Capture + Download
    # -----------------------------------------

    def prepare_audio(self):

        page = self.browser.get_page()

        url = self.extractor.extract(page)

        return self.downloader.download(url)