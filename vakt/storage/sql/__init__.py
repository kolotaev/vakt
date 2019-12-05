"""
SQL Storage for Policies.
"""

import logging

from sqlalchemy import and_, or_, literal, func
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
        self.dialect = self.session.bind.engine.dialect.name

    def add(self, policy):
        try:
            policy_model = PolicyModel.from_policy(policy)
            self.session.add(policy_model)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            log.error('Error trying to create already existing policy with UID=%s.', policy.uid)
            raise PolicyExistsError(policy.uid)
        # todo - figure out why FlushError is raised instead of IntegrityError on PyPy tests
        except FlushError as e:
            if 'conflicts with persistent instance' in str(e):
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
        cur = self.session.query(PolicyModel).order_by(PolicyModel.uid.asc()).slice(offset, offset + limit)
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
                PolicyModel.actions.any(PolicyActionModel.action_string.like('%{}%'.format(inquiry.action))),
                PolicyModel.resources.any(PolicyResourceModel.resource_string.like('%{}%'.format(inquiry.resource))),
                PolicyModel.subjects.any(PolicySubjectModel.subject_string.like('%{}%'.format(inquiry.subject))))
        elif isinstance(checker, StringExactChecker):
            return cur.filter(
                PolicyModel.type == TYPE_STRING_BASED,
                PolicyModel.actions.any(PolicyActionModel.action_string == inquiry.action),
                PolicyModel.resources.any(PolicyResourceModel.resource_string == inquiry.resource),
                PolicyModel.subjects.any(PolicySubjectModel.subject_string == inquiry.subject))
        elif isinstance(checker, RegexChecker):
            if not self._supports_regex_operator():
                return cur.filter(PolicyModel.type == TYPE_STRING_BASED)
            return cur.filter(
                PolicyModel.type == TYPE_STRING_BASED,
                PolicyModel.actions.any(
                    or_(
                        and_(PolicyActionModel.action_regex.is_(None),
                             PolicyActionModel.action_string == inquiry.action),
                        and_(PolicyActionModel.action_regex.isnot(None),
                             self._regex_operation(inquiry.action, PolicyActionModel.action_regex))
                    ),
                ),
                PolicyModel.resources.any(
                    or_(
                        and_(PolicyResourceModel.resource_regex.is_(None),
                             PolicyResourceModel.resource_string == inquiry.resource),
                        and_(PolicyResourceModel.resource_regex.isnot(None),
                             self._regex_operation(inquiry.resource, PolicyResourceModel.resource_regex))
                    ),
                ),
                PolicyModel.subjects.any(
                    or_(
                        and_(PolicySubjectModel.subject_regex.is_(None),
                             PolicySubjectModel.subject_string == inquiry.subject),
                        and_(PolicySubjectModel.subject_regex.isnot(None),
                             self._regex_operation(inquiry.subject, PolicySubjectModel.subject_regex))
                    ),
                )
            )
        elif isinstance(checker, RulesChecker):
            return cur.filter(PolicyModel.type == TYPE_RULE_BASED)
        elif not checker:
            return cur
        else:
            log.error('Provided Checker type is not supported.')
            raise UnknownCheckerType(checker)

    def _supports_regex_operator(self):
        """
        Does database support regex operator?
        """
        return self.dialect in ['mysql', 'postgresql', 'oracle']

    def _regex_operation(self, left, right):
        """
        Get database-specific regex operation.
        Don't forget to check if there is a support for regex operator before using it.
        """
        if self.dialect == 'mysql':
            return literal(left).op('REGEXP BINARY', is_comparison=True)(right)
        elif self.dialect == 'postgresql':
            return literal(left).op('~', is_comparison=True)(right)
        elif self.dialect == 'oracle':
            return func.REGEXP_LIKE(left, right)
        return None
