import os
import requests

from audio.download_result import DownloadResult
from utils.logger import logger


class AudioDownloader:

    def __init__(self):

        self.download_folder = "downloads"

        os.makedirs(self.download_folder, exist_ok=True)

    def download(self, url):

        logger.info("Downloading audio...")

        filename = url.split("/")[-1]

        local_path = os.path.join(
            self.download_folder,
            filename
        )

        # Already downloaded
        if os.path.exists(local_path):

            logger.info("Audio already exists.")

            return DownloadResult(
                success=True,
                url=url,
                filename=filename,
                local_path=local_path,
                message="Using cached audio."
            )

        try:

            with requests.get(
                url,
                stream=True,
                timeout=120
            ) as response:

                response.raise_for_status()

                with open(local_path, "wb") as file:

                    for chunk in response.iter_content(8192):

                        if chunk:

                            file.write(chunk)

            logger.info(f"Saved audio: {local_path}")

            return DownloadResult(
                success=True,
                url=url,
                filename=filename,
                local_path=local_path,
                message="Audio downloaded successfully."
            )

        except Exception as error:

            logger.exception("Audio download failed.")

            return DownloadResult(
                success=False,
                url=url,
                filename=filename,
                local_path=None,
                message=str(error)
            )