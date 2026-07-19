from vision.page_scanner import PageScanner
from vision.page_classifier import PageClassifier
from vision.page_memory import PageMemory
from vision.semantic_labeler import SemanticLabeler


class VisionEngine:

    def __init__(self):

        self.scanner = PageScanner()
        self.classifier = PageClassifier()
        self.labeler = SemanticLabeler()
        self.memory = PageMemory()

    def observe(self, page):

        snapshot = self.scanner.scan(page)

        snapshot.page_type = self.classifier.classify(snapshot)

        snapshot = self.labeler.label(snapshot)

        self.memory.remember(snapshot)

        return snapshot