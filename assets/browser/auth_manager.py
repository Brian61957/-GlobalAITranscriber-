from browser.session_storage import SessionStorage


class AuthManager:

    def __init__(self):

        self.storage = SessionStorage()

    def has_saved_session(self):

        return self.storage.exists()

    def session_path(self):

        return self.storage.path()