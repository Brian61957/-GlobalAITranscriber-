class ClipManager:

    def __init__(self):

        self.current_clip = 0
        self.total_clips = 0
        self.clips = []

    def load(self, clips):

        self.clips = clips
        self.total_clips = len(clips)
        self.current_clip = 0

    def current(self):

        if not self.clips:
            return None

        return self.clips[self.current_clip]

    def next(self):

        if self.current_clip + 1 < self.total_clips:
            self.current_clip += 1
            return True

        return False

    def has_next(self):

        return self.current_clip + 1 < self.total_clips

    def progress(self):

        if self.total_clips == 0:
            return 0

        return (self.current_clip + 1) / self.total_clips