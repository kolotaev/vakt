"""
SQL Storage for Policies.
"""

import logging

from sqlalchemy.exc import IntegrityError

from .model import PolicyModel
from ..abc import Storage
from ...exceptions import PolicyExistsError

log = logging.getLogger(__name__)


class SQLStorage(Storage):
    """Stores all policies in SQL Database"""

    def __init__(self, scoped_session):
        """
            Initialize SQL Storage

            :param scoped_session: SQL Alchemy scoped session
        """
        self.session = scoped_session

    def add(self, policy):
        try:
            policy_model = PolicyModel.from_policy(policy)
            self.session.add(policy_model)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            log.error('Error trying to create already existing policy with UID=%s.', policy.uid)
            raise PolicyExistsError(policy.uid)
        log.info('Added Policy: %s', policy)

    def get(self, uid):
        policy_model = self.session.query(PolicyModel).get(uid)
        if not policy_model:
            return None
        return policy_model.to_policy()

    def get_all(self, limit, offset):
        self._check_limit_and_offset(limit, offset)
        cur = self.session.query(PolicyModel).slice(offset, offset + limit)
        for policy_model in cur:
            yield policy_model.to_policy()

    def find_for_inquiry(self, inquiry, checker=None):
        pass

    def update(self, policy):
        try:
            policy_model = self.session.query(PolicyModel).get(policy.uid)
            if not policy_model:
                return
            policy_model.update(policy)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        log.info('Updated Policy with UID=%s. New value is: %s', policy.uid, policy)

    def delete(self, uid):
        self.session.query(PolicyModel).filter(PolicyModel.uid == uid).delete()
        log.info('Deleted Policy with UID=%s.', uid)
