"""
MongoDB Storage and Migrations for Policies.
"""

import logging
import copy

import bson.json_util as b_json
from pymongo.errors import DuplicateKeyError
import jsonpickle.tags

from ..storage.abc import Storage, Migration
from ..exceptions import PolicyExistsError, UnknownCheckerType, Irreversible
from ..policy import Policy
from ..checker import StringExactChecker, StringFuzzyChecker, RegexChecker


DEFAULT_COLLECTION = 'vakt_policies'

log = logging.getLogger(__name__)


class MongoStorage(Storage):
    """Stores all policies in MongoDB"""

    def __init__(self, client, db_name, collection=DEFAULT_COLLECTION):
        self.client = client
        self.database = self.client[db_name]
        self.collection = self.database[collection]
        self.condition_fields = [
            'actions',
            'subjects',
            'resources',
        ]

    def add(self, policy):
        try:
            self.collection.insert_one(self.__prepare_doc(policy))
        except DuplicateKeyError:
            log.error('Error trying to create already existing policy with UID=%s.', policy.uid)
            raise PolicyExistsError(policy.uid)
        log.info('Added Policy: %s.', policy)

    def get(self, uid):
        ret = self.collection.find_one(uid)
        if not ret:
            return None
        return self.__prepare_from_doc(ret)

    def get_all(self, limit, offset):
        self._check_limit_and_offset(limit, offset)
        cur = self.collection.find(limit=limit, skip=offset)
        return self.__feed_policies(cur)

    def find_for_inquiry(self, inquiry, checker=None):
        q_filter = self._create_filter(inquiry, checker)
        cur = self.collection.find(q_filter)
        return self.__feed_policies(cur)

    def update(self, policy):
        uid = policy.uid
        self.collection.update_one(
            {'_id': uid},
            {"$set": self.__prepare_doc(policy)},
            upsert=False)
        log.info('Updated Policy with UID=%s. New value is: %s.', uid, policy)

    def delete(self, uid):
        self.collection.delete_one({'_id': uid})
        log.info('Deleted Policy with UID=%s.', uid)

    def _create_filter(self, inquiry, checker):
        """
        Returns proper query-filter based on the checker type.
        """
        if isinstance(checker, StringFuzzyChecker):
            return self.__string_query_on_conditions('$regex', lambda field: getattr(inquiry, field))
        elif isinstance(checker, StringExactChecker):
            return self.__string_query_on_conditions('$eq', lambda field: getattr(inquiry, field))
            # We do not use Reverse-regexp match since it's not implemented yet in MongoDB.
            # Doing it via Javascript function gives no benefits over Vakt final Guard check.
            # See: https://jira.mongodb.org/browse/SERVER-11947
        elif isinstance(checker, RegexChecker) or not checker:  # opt to RegexChecker as default.
            return {}
        else:
            log.error('Provided Checker type is not supported.')
            raise UnknownCheckerType(checker)

    def __string_query_on_conditions(self, operator, get_value):
        """
        Construct MongoDB query.
        """
        conditions = []
        for field in self.condition_fields:
            conditions.append(
                {
                    field: {
                        '$elemMatch': {
                            operator: get_value(field.rstrip('s'))
                        }
                    }
                }
            )
        return {"$and": conditions}

    @staticmethod
    def __prepare_doc(policy):
        """
        Prepare Policy object as a document for insertion.
        """
        # todo - add dict inheritance
        doc = b_json.loads(policy.to_json())
        doc['_id'] = policy.uid
        return doc

    @staticmethod
    def __prepare_from_doc(doc):
        """
        Prepare Policy object as a return from MongoDB.
        """
        # todo - add dict inheritance
        del doc['_id']
        return Policy.from_json(b_json.dumps(doc))

    def __feed_policies(self, cursor):
        """
        Yields Policies from the given cursor.
        """
        for doc in cursor:
            yield self.__prepare_from_doc(doc)


##############
# Migrations #
##############

class Migration0To1x1x0(Migration):
    """
    Migration between versions 0 and 1.1.0
    """

    def __init__(self, storage):
        self.storage = storage
        self.index_name = lambda i: i + '_idx'
        self.multi_key_indices = [
            'actions',
            'subjects',
            'resources',
        ]

    @property
    def order(self):
        return 1

    def up(self):
        # MongoDB automatically creates a multikey index if any indexed field is an array;
        # https://docs.mongodb.com/manual/core/index-multikey/#create-multikey-index
        for field in self.multi_key_indices:
            self.storage.collection.create_index(field, name=self.index_name(field))

    def down(self):
        for field in self.multi_key_indices:
            self.storage.collection.drop_index(self.index_name(field))


class Migration1x1x0To1x1x1(Migration):
    """
    Migration between versions 1.1.0 and 1.1.1
    """

    def __init__(self, storage):
        self.storage = storage
        self._type_marker = jsonpickle.tags.OBJECT

    @property
    def order(self):
        return 2

    def up(self):
        def process(doc):
            doc_to_save = copy.deepcopy(doc)
            rules_to_save = {}
            for name, rule_str in doc['rules'].items():
                rule = b_json.loads(rule_str)
                rule_to_save = {self._type_marker: rule['type']}
                rule_to_save.update(rule['contents'])
                rules_to_save[name] = rule_to_save
            doc_to_save['rules'] = rules_to_save
            return doc_to_save
        self._docs_iteration(processor=process)

    def down(self):
        def process(doc):
            doc_to_save = copy.deepcopy(doc)
            rules_to_save = {}
            for name, rule in doc['rules'].items():
                rule_type = rule[self._type_marker]
                rule_contents = rule.copy()
                del rule_contents[self._type_marker]
                rule_to_save = {'type': rule_type, 'contents': {}}
                # check if we are dealing with 3-rd party or custom rules
                if not rule_type.startswith('vakt.rules.'):
                    for value in rule_contents.values():
                        # if rule has non-primitive data as its contents - we can't revert it to 1.1.0
                        if isinstance(value, dict) and jsonpickle.tags.RESERVED.intersection(value.keys()):
                            raise Irreversible('Custom rule class contains non-primitive data %s' % value)
                # vakt's own RegexMatchRule couldn't be stored in mongo because is has non-primitive data,
                # so it's impossible to put it to storage if we revert time back to 1.1.0
                elif rule_type == 'vakt.rules.string.RegexMatchRule':
                    raise Irreversible('vakt.rules.string.RegexMatchRule could not be stored in v1.1.0')
                rule_to_save['contents'].update(rule_contents)
                rules_to_save[name] = b_json.dumps(rule_to_save, sort_keys=True)
            # report or save document
            doc_to_save['rules'] = rules_to_save
            return doc_to_save
        self._docs_iteration(processor=process)

    def _docs_iteration(self, processor):
        failed_policies = []
        cur = self.storage.collection.find()
        for doc in cur:
            try:
                log.info('Trying to migrate Policy with UID: %s' % doc['uid'])
                new_doc = processor(doc)
                self.storage.collection.update_one({'_id': new_doc['uid']}, {"$set": new_doc}, upsert=False)
                log.info('Policy with UID was migrated: %s' % doc['uid'])
            except Irreversible as e:
                log.warning('Irreversible Policy. %s. Mongo doc: %s', e, doc)
                failed_policies.append(doc)
            except Exception as e:
                log.exception('Unexpected exception occurred while migrating Policy: %s', doc)
                failed_policies.append(doc)
        if failed_policies:
            msg = "\n".join([
                'Migration was unable to convert some Policies, but they were left in the database as-is. ' +
                'Some of them are custom ones, some are just malformed JSON docs.',
                'You must convert them manually or delete entirely. See above log output for details of migration.',
                'Mongo IDs of failed Policies are: %s' % [p['_id'] for p in failed_policies]
            ])
            log.error(msg)
