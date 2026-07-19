"""
Per-domain session storage.

Each platform the user logs into gets its own session file, named
after the domain (e.g. speech.intron.health.json, app.appen.com.json).
This means logging into one platform never overwrites another, and the
tool can maintain persistent logins for as many platforms as you use.
"""

import re
from pathlib import Path

SESSION_DIR = Path("browser/sessions")
SESSION_DIR.mkdir(parents=True, exist_ok=True)


def _domain_to_filename(domain: str) -> str:
    """Converts a domain like speech.intron.health -> speech.intron.health.json"""
    safe = re.sub(r"[^\w.\-]", "_", domain.lower())
    return f"{safe}.json"


class SessionStorage:

    def __init__(self, domain: str = "default"):
        self.domain = domain
        self.session_file = SESSION_DIR / _domain_to_filename(domain)

    def exists(self) -> bool:
        return self.session_file.exists()

    def path(self) -> str:
        return str(self.session_file)

    def delete(self):
        if self.session_file.exists():
            self.session_file.unlink()

    @classmethod
    def for_url(cls, url: str) -> "SessionStorage":
        """Create a SessionStorage keyed to the domain of a given URL."""
        from urllib.parse import urlparse
        try:
            domain = urlparse(url).hostname or "default"
        except Exception:
            domain = "default"
        return cls(domain)

    @classmethod
    def list_all(cls):
        """Return all saved session domains."""
        return [f.stem for f in SESSION_DIR.glob("*.json")]
