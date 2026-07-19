from pathlib import Path

SESSION_DIR = Path("browser/sessions")
SESSION_DIR.mkdir(parents=True, exist_ok=True)

SESSION_FILE = SESSION_DIR / "intron_session.json"


class SessionStorage:

    def exists(self):

        return SESSION_FILE.exists()

    def path(self):

        return str(SESSION_FILE)

    def delete(self):

        if SESSION_FILE.exists():
            SESSION_FILE.unlink()