from abc import ABC, abstractmethod


class BasePlatform(ABC):

    @abstractmethod
    def open_project(self, url):
        pass

    @abstractmethod
    def read_project(self):
        pass

    @abstractmethod
    def locate_audio(self):
        pass

    @abstractmethod
    def locate_draft(self):
        pass

    @abstractmethod
    def next_clip(self):
        pass