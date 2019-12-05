from ..util import Subject


class ObservableMutationStorage(Subject):
    """
    Wraps Storage.
    Implements mutation part of Storage interface as a notifier of subscribers.
    Notifies observers when mutation method is called on Storage.
    Read part of Storage interface is a simple proxy.
    """
    def __init__(self, storage):
        self.storage = storage
        super().__init__()

    def add(self, policy):
        res = self.storage.add(policy)
        self.notify()
        return res

    def update(self, policy):
        res = self.storage.update(policy)
        self.notify()
        return res

    def delete(self, uid):
        res = self.storage.delete(uid)
        self.notify()
        return res

    def get(self, uid):
        return self.storage.get(uid)

    def get_all(self, limit, offset):
        return self.storage.get_all(limit, offset)

    def retrieve_all(self, *args, **kwargs):
        return self.storage.retrieve_all(*args, **kwargs)

    def find_for_inquiry(self, inquiry, checker=None):
        return self.storage.find_for_inquiry(inquiry, checker)
