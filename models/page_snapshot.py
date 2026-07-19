from dataclasses import dataclass, field

from typing import List

from models.page_element import PageElement


@dataclass
class PageSnapshot:

    page_type: str = "Unknown"

    title: str = ""

    url: str = ""

    text: str = ""

    buttons: List[PageElement] = field(default_factory=list)

    textboxes: List[PageElement] = field(default_factory=list)

    dropdowns: List[PageElement] = field(default_factory=list)

    audio_players: List[PageElement] = field(default_factory=list)

    links: List[PageElement] = field(default_factory=list)

    headings: List[PageElement] = field(default_factory=list)

    labels: List[PageElement] = field(default_factory=list)

    checkboxes: List[PageElement] = field(default_factory=list)

    radio_buttons: List[PageElement] = field(default_factory=list)