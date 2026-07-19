import re
from urllib.parse import urlparse

# Add known-legitimate transcription/annotation platforms here as you
# use them. This isn't required for the app to work -- it just lets
# recognized platforms skip the "unfamiliar site" warning.
KNOWN_PLATFORMS = [
    "intron.health",
    "app.intron.io",
    "intron.io",
]

# Patterns that are common in phishing/lookalike URLs. None of these
# prove a site is malicious on their own -- they're just reasons to
# slow down and confirm before an automated browser starts typing into it.
SUSPICIOUS_PATTERNS = [
    (r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", "the address is a raw IP, not a domain name"),
    (r"xn--", "the domain uses punycode (can be used to fake familiar-looking domains)"),
    (r"-{2,}", "the domain has an unusually long run of hyphens"),
    (r"^(bit\.ly|tinyurl\.com|t\.co|goo\.gl)$", "it's a link shortener, so the real destination is hidden"),
]


class PlatformVerifier:
    """
    A lightweight, honest sanity check on a URL before the AI starts
    interacting with it. This is NOT a security guarantee -- it can't
    prove a site is legitimate. It only catches a few common red flags
    and otherwise asks the user to confirm anything it doesn't recognize.
    """

    def verify(self, url):
        parsed = urlparse(url.strip())
        domain = (parsed.hostname or "").lower()

        issues = []

        if parsed.scheme != "https":
            issues.append("The URL doesn't use HTTPS, so the connection isn't encrypted.")

        for pattern, reason in SUSPICIOUS_PATTERNS:
            if re.search(pattern, domain):
                issues.append(f"The domain looks unusual: {reason}.")

        is_known = any(domain == known or domain.endswith("." + known) for known in KNOWN_PLATFORMS)

        if is_known:
            status = "known"
        elif issues:
            status = "suspicious"
        else:
            status = "unverified"

        return {
            "domain": domain,
            "status": status,  # "known" | "unverified" | "suspicious"
            "issues": issues,
        }
