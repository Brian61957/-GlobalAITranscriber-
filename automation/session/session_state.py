class SessionState:

    def __init__(self):

        self.logged_in = False

        self.project_loaded = False

        self.current_clip = 0

        self.total_clips = 0

        self.status = "Idle"

    def update(self, **kwargs):

        for key, value in kwargs.items():

            setattr(self, key, value)