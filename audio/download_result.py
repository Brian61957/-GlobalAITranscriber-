from dataclasses import dataclass


@dataclass
class DownloadResult:

    success: bool

    url: str = ""

    local_path: str = ""

    filename: str = ""

    message: str = ""