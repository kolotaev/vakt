import json

from sqlalchemy import Column, Integer, SmallInteger, String, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import declarative_base, relationship

from ...policy import Policy, ALLOW_ACCESS, DENY_ACCESS, TYPE_STRING_BASED
from ...rules.base import Rule
from ...parser import compile_regex

Base = declarative_base()


class PolicySubjectModel(Base):
    """Storage model for policy subjects"""

    __tablename__ = 'vakt_policy_subjects'

    id = Column(Integer, primary_key=True)
    uid = Column(String(255), ForeignKey('vakt_policies.uid', ondelete='CASCADE'))
    subject = Column(JSON(), comment='JSON value for rule-based policies')
    subject_string = Column(String(255), index=True, comment='Initial string value for string-based policies')
    subject_regex = Column(String(520),
                           index=True,
                           comment='Regexp from initial string value for string-based policies')


class PolicyResourceModel(Base):
    """Storage model for policy resources"""

    __tablename__ = 'vakt_policy_resources'

    id = Column(Integer, primary_key=True)
    uid = Column(String(255), ForeignKey('vakt_policies.uid', ondelete='CASCADE'))
    resource = Column(JSON(), comment='JSON value for rule-based policies')
    resource_string = Column(String(255), index=True, comment='Initial string value for string-based policies')
    resource_regex = Column(String(520),
                            index=True,
                            comment='Regexp from initial string value for string-based policies')


class PolicyActionModel(Base):
    """Storage model for policy actions"""

    __tablename__ = 'vakt_policy_actions'

    id = Column(Integer, primary_key=True)
    uid = Column(String(255), ForeignKey('vakt_policies.uid', ondelete='CASCADE'))
    action = Column(JSON(), comment='JSON value for rule-based policies')
    action_string = Column(String(255), index=True, comment='Initial string value for string-based policies')
    action_regex = Column(String(520),
                          index=True,
                          comment='Regexp from initial string value for string-based policies')


class PolicyModel(Base):
    """Storage model for policy"""

    __tablename__ = 'vakt_policies'

    uid = Column(String(255), primary_key=True)
    type = Column(SmallInteger)
    description = Column(Text())
    effect = Column(Boolean())
    context = Column(JSON())
    subjects = relationship(PolicySubjectModel, passive_deletes=True, lazy='joined')
    resources = relationship(PolicyResourceModel, passive_deletes=True, lazy='joined')
    actions = relationship(PolicyActionModel, passive_deletes=True, lazy='joined')

    @classmethod
    def from_policy(cls, policy):
        """
            Instantiate from policy object

            :param policy: object of type policy
        """
        rvalue = cls()
        return cls._save(policy, model=rvalue)

    def update(self, policy):
        """
            Update object attributes to match given policy

            :param policy: object of type policy
        """
        self._save(policy, model=self)

    def to_policy(self):
        """
            Create a policy object

            :return: object of type `Policy`
        """
        return Policy(uid=self.uid,
                      effect=ALLOW_ACCESS if self.effect else DENY_ACCESS,
                      description=self.description,
                      context=Rule.from_json(self.context),
                      subjects=[
                          self._policy_element_from_db(self.type, x.subject, x.subject_string)
                          for x in self.subjects
                      ],
                      resources=[
                          self._policy_element_from_db(self.type, x.resource, x.resource_string)
                          for x in self.resources
                      ],
                      actions=[
                          self._policy_element_from_db(self.type, x.action, x.action_string)
                          for x in self.actions
                      ])

    @classmethod
    def _save(cls, policy, model):
        """
            Helper to create PolicyModel from Policy object for add and update operations.

            :param policy: object of type Policy
            :param model: object of type PolicyModel
        """
        policy_json = policy.to_json()
        policy_dict = json.loads(policy_json)
        model.uid = policy_dict['uid']
        model.type = policy_dict['type']
        model.effect = policy_dict['effect'] == ALLOW_ACCESS
        model.description = policy_dict['description']
        model.context = json.dumps(policy_dict['context'])
        model.subjects = [
            PolicySubjectModel(subject=x, subject_string=string, subject_regex=compiled)
            for y in policy_dict['subjects']
            for (x, string, compiled) in cls._policy_element_to_db(policy, y)
        ]
        model.resources = [
            PolicyResourceModel(resource=x, resource_string=string, resource_regex=compiled)
            for y in policy_dict['resources']
            for (x, string, compiled) in cls._policy_element_to_db(policy, y)
        ]
        model.actions = [
            PolicyActionModel(action=x, action_string=string, action_regex=compiled)
            for y in policy_dict['actions']
            for (x, string, compiled) in cls._policy_element_to_db(policy, y)
        ]
        return model

    @classmethod
    def _policy_element_to_db(cls, policy, el):
        json_value, string_value, compiled = None, None, None
        if policy.type == TYPE_STRING_BASED:
            string_value = el
            if policy.start_tag in el and policy.end_tag in el:
                compiled = compile_regex(el, policy.start_tag, policy.end_tag).pattern
        else:  # it's a rule-based policy and it's value is a json
            json_value = json.dumps(el)
        yield (json_value, string_value, compiled)

    @classmethod
    def _policy_element_from_db(cls, policy_type, element_json, element_string):
        if policy_type == TYPE_STRING_BASED:
            return element_string
        return Rule.from_json(element_json)
