from abc import ABC, abstractmethod


class IManager(ABC):
    @abstractmethod
    def get(self, id):
        pass

    @abstractmethod
    def get_all(self, limit, offset):
        pass

    @abstractmethod
    def create(self, policy):
        pass

    @abstractmethod
    def update(self, policy):
        pass

    @abstractmethod
    def delete(self, id):
        pass
