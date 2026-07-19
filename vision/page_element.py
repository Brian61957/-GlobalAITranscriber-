from dataclasses import dataclass


@dataclass
class PageElement:

    element_type: str = ""

    text: str = ""

    selector: str = ""

    role: str = ""

    visible: bool = True

    enabled: bool = True

    value: str = ""

    placeholder: str = ""

    aria_label: str = ""

    title: str = ""

    element_id: str = ""

    classes: str = ""

    name: str = ""

    data_testid: str = ""