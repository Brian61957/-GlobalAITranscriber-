class PageMemory:

    def __init__(self):

        self.last_snapshot = None

    def remember(self, snapshot):

        self.last_snapshot = snapshot

    def recall(self):

        return self.last_snapshot