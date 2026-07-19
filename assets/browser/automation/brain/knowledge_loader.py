import json
from pathlib import Path


class KnowledgeLoader:

    def __init__(self):

        root = Path(__file__).resolve().parent.parent.parent

        self.knowledge_path = root / "knowledge"

    def load(self, filename):

        file = self.knowledge_path / filename

        with open(file, "r", encoding="utf-8") as f:

            return json.load(f)