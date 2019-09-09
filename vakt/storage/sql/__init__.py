"""
SQL Storage for Policies.
"""

import json
import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

from .model import PolicyModel, PolicyActionModel, PolicyResourceModel, PolicySubjectModel
from ..abc import Storage
from ...checker import StringExactChecker, StringFuzzyChecker, RegexChecker, RulesChecker
from ...exceptions import PolicyExistsError, UnknownCheckerType
from ...policy import TYPE_STRING_BASED, TYPE_RULE_BASED

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
        cur = self._get_filtered_cursor(inquiry, checker)
        for policy_model in cur:
            yield policy_model.to_policy()

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

    def _get_filtered_cursor(self, inquiry, checker):
        """
            Returns cursor with proper query-filter based on the checker type.
        """
        cur = self.session.query(PolicyModel)
        if isinstance(checker, StringFuzzyChecker):

            return cur.filter(
                PolicyModel.type == TYPE_STRING_BASED,
                PolicyModel.subjects.any(PolicySubjectModel.subject.like("%{}%".format(inquiry.subject))),
                PolicyModel.resources.any(PolicyResourceModel.resource.like("%{}%".format(inquiry.resource))),
                PolicyModel.actions.any(PolicyActionModel.action.like("%{}%".format(inquiry.action))))
        elif isinstance(checker, StringExactChecker):
            # A string is converted to a JSON string before inserting
            return cur.filter(
                PolicyModel.type == TYPE_STRING_BASED,
                PolicyModel.subjects.any(PolicySubjectModel.subject == json.dumps(inquiry.subject)),
                PolicyModel.resources.any(PolicyResourceModel.resource == json.dumps(inquiry.resource)),
                PolicyModel.actions.any(PolicyActionModel.action == json.dumps(inquiry.action)))
        elif isinstance(checker, RegexChecker):
            return cur.filter(
                PolicyModel.type == TYPE_STRING_BASED)
        elif isinstance(checker, RulesChecker):
            return cur.filter(
                PolicyModel.type == TYPE_RULE_BASED)
        elif not checker:
            return cur
        else:
            log.error('Provided Checker type is not supported.')
            raise UnknownCheckerType(checker)
