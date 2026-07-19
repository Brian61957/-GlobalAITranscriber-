from dataclasses import dataclass, field

from vision.page_element import PageElement


@dataclass
class PageSnapshot:

    title: str = ""

    url: str = ""

    page_type: str = ""

    headings: list[str] = field(default_factory=list)

    buttons: list[PageElement] = field(default_factory=list)

    textboxes: list[PageElement] = field(default_factory=list)

    audio_players: list[PageElement] = field(default_factory=list)

    dropdowns: list[PageElement] = field(default_factory=list)

    labels: list[str] = field(default_factory=list)