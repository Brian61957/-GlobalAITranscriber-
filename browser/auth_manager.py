from browser.session_storage import SessionStorage


class AuthManager:

    def __init__(self, session_storage: SessionStorage = None):
        self.storage = session_storage or SessionStorage("default")

    def has_saved_session(self):
        return self.storage.exists()

    def session_path(self):
        return self.storage.path()

    def delete_session(self):
        self.storage.delete()
