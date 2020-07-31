"""
Redis storage for Policies.
"""

import logging
import pickle
import itertools

from ..storage.abc import Storage
from ..policy import Policy
from ..exceptions import PolicyExistsError


log = logging.getLogger(__name__)

DEFAULT_COLLECTION = 'vakt_policies'


class JSONSerializer:
    """
    Serializes/de-serializes policies to JSON for Redis storage
    """
    @staticmethod
    def serialize(policy):
        return policy.to_json()

    @staticmethod
    def deserialize(data):
        return Policy.from_json(data.decode('utf-8'))


class PickleSerializer:
    """
    Serializes/de-serializes policies Python pickle representation for Redis storage
    """
    def __init__(self, *args, **kwargs):
        """
        Use args and kwargs to pass them to customized pickle module calls.
        """
        self.args = args
        self.kwargs = kwargs

    def serialize(self, policy):
        return pickle.dumps(policy, *self.args, **self.kwargs)

    def deserialize(self, data):
        return pickle.loads(data, **self.kwargs)


class RedisStorage(Storage):
    """
    Stores Policies in Redis.

    Stores all policies in a single hash whose name is a `collection` argument.
    Each filed in this hash is a Policy's UID and the value of this key is a serialized Policy representation.
    """

    def __init__(self, client, collection=DEFAULT_COLLECTION, serializer=None):
        self.client = client
        self.collection = collection
        self.sr = serializer
        if serializer is None:
            self.sr = PickleSerializer()

    def add(self, policy):
        uid = policy.uid
        try:
            done = self.client.hsetnx(self.collection, uid, self.sr.serialize(policy))
            if done == 0:
                log.error('Error trying to create already existing policy with UID=%s.', uid)
                raise PolicyExistsError(uid)
        except Exception:
            log.exception('Error trying to create already existing policy with UID=%s.', uid)
            raise PolicyExistsError(uid)
        log.info('Added Policy: %s', policy)

    def get(self, uid):
        ret = self.client.hget(self.collection, uid)
        if not ret:
            return None
        return self.sr.deserialize(ret)

    def get_all(self, limit, offset):
        # According to docs https://redis.io/commands/scan#the-count-option
        # Redis doesn't guarantee the exact number of elements returned,
        # so we opt to fetching all data and manual slicing on the client side.
        self._check_limit_and_offset(limit, offset)
        data = self.client.hgetall(self.collection)
        sliced = itertools.islice(data.items(), offset, limit+offset)
        return self.__feed_policies(dict(sliced))

    def find_for_inquiry(self, inquiry, checker=None):
        data = self.client.hgetall(self.collection)
        if not data:
            return []
        return self.__feed_policies(data)

    def update(self, policy):
        uid = policy.uid
        lua = """
        local exists = redis.call('HEXISTS', KEYS[1], ARGV[1])
        if exists == 1 then
            return redis.call('HSET', KEYS[1], ARGV[1], ARGV[2])
        end
        return 0
        """
        update_policy = self.client.register_script(lua)
        try:
            res = update_policy(keys=[self.collection], args=[uid, self.sr.serialize(policy)])
            if res == 1:
                log.info('Updated Policy with UID=%s. New value is: %s', uid, policy)
        except Exception as e:
            log.exception('Error trying to update policy with UID=%s.', uid)
            raise e

    def delete(self, uid):
        res = self.client.hdel(self.collection, uid)
        if res == 0:
            log.info('Nothing to delete by UID=%s', uid)
        else:
            log.info('Deleted Policy with UID=%s', uid)

    def __feed_policies(self, data):
        """
        Yields Policies from the given cursor.
        """
        for uid in data:
            yield self.sr.deserialize(data[uid])
