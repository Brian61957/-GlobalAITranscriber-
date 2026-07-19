from urllib.parse import urlparse


def normalize_url(raw_url):
    """
    Cleans up a pasted URL so it's actually navigable:
      - strips whitespace and accidental surrounding quotes
      - adds "https://" if the scheme was left off (very common when
        copying a link from an address bar or a "copy link" button)

    Raises ValueError with a clear, user-facing message if the result
    still isn't a usable URL.
    """
    if not raw_url:
        raise ValueError("Please paste a project URL.")

    url = raw_url.strip().strip('"').strip("'")

    if " " in url:
        raise ValueError("That doesn't look like a valid URL (it contains spaces).")

    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)

    if not parsed.hostname or "." not in parsed.hostname:
        raise ValueError(
            f"'{raw_url}' doesn't look like a valid URL. "
            "Make sure you copied the full link, including the domain."
        )

    return url
