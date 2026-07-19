"""
run_cli.py

Standalone CLI test of the full Global AI Transcriber workflow:

    Paste Instruction URL
        -> Open instruction page
        -> Read EVERYTHING
        -> Understand project (AI)
        -> Find "Good Luck" / "Start"
        -> Click it
        -> Wait until transcription page appears
        -> Detect + download the clip's audio
        -> Transcribe it
        -> Print the result

Run with:
    python run_cli.py
"""

import sys

from browser.browser_manager import BrowserManager
from automation.project.project_reader import ProjectReader
from automation.project.project_navigator import ProjectNavigator
from audio.audio_downloader import AudioDownloader
from speech.speech_manager import SpeechManager
from utils.logger import logger


def main():
    url = input("Paste the Instruction URL: ").strip()

    if not url:
        print("No URL provided. Exiting.")
        sys.exit(1)

    browser = BrowserManager()

    try:
        # ------------------------------------------------------
        # 1. Open instruction page
        # ------------------------------------------------------
        browser.start()
        browser.open_project(url)
        page = browser.get_page()

        # ------------------------------------------------------
        # 2 & 3. Read EVERYTHING + Understand project (AI)
        # ------------------------------------------------------
        profile = ProjectReader(page).read()

        print("\n=== PROJECT UNDERSTANDING ===")
        for key, value in profile.summary().items():
            print(f"{key}: {value}")
        if profile.dos:
            print(f"dos: {profile.dos}")
        if profile.donts:
            print(f"donts: {profile.donts}")
        print("==============================\n")

        # ------------------------------------------------------
        # 4 & 5. Find "Good Luck" / "Start", click it, wait for
        #        the transcription page to appear
        # ------------------------------------------------------
        ProjectNavigator(page).enter_task()

        # A fresh page may fire its own audio/media requests once
        # loaded — ignore anything captured before this point.
        browser.clear_media_requests()

        # ------------------------------------------------------
        # 6. Begin transcription
        # ------------------------------------------------------
        print("Waiting for the task's audio to load...")

        media_url = browser.wait_for_media_request(timeout=30)

        print(f"Audio detected: {media_url}")

        download = AudioDownloader().download(media_url)

        if not download.success:
            print(f"Audio download failed: {download.message}")
            sys.exit(1)

        print(f"Audio saved to: {download.local_path}")

        result = SpeechManager().transcribe(
            audio_file=download.local_path,
            instructions=profile.instructions,
            language=(profile.language or None),
            profile=profile,
        )

        if not result.success:
            print(f"Transcription failed: {result.error}")
            sys.exit(1)

        print("\n=== TRANSCRIPT ===")
        print(result.transcript)
        print("===================\n")

        # Keep the login session so the next run skips re-authenticating
        browser.save_session()

        input("Press Enter to close the browser...")

    except Exception:
        logger.exception("Workflow failed.")
        raise

    finally:
        browser.close()


if __name__ == "__main__":
    main()
