class BrainMemory:

    def __init__(self):

        self.data = {}

    def remember(self, key, value):

        self.data[key] = value

    def recall(self, key, default=None):

        return self.data.get(key, default)

    def clear(self):

        self.data.clear()

    def export(self):

        return self.data.copy()