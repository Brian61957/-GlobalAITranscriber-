from dataclasses import dataclass, field
from typing import Dict


@dataclass
class PageElement:

    role: str = ""

    tag: str = ""

    selector: str = ""

    text: str = ""

    visible: bool = True

    enabled: bool = True

    element_id: str = ""

    name: str = ""

    aria_label: str = ""

    title: str = ""

    placeholder: str = ""

    value: str = ""

    href: str = ""

    attributes: Dict[str, str] = field(default_factory=dict)