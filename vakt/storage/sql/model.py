import json

from sqlalchemy import Column, Integer, SmallInteger, String, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from ...policy import Policy, ALLOW_ACCESS, DENY_ACCESS, TYPE_STRING_BASED
from ...rules.base import Rule
from ...parser import compile_regex


Base = declarative_base()


class PolicySubjectModel(Base):
    """Storage model for policy subjects"""

    __tablename__ = 'vakt_policy_subjects'

    id = Column(Integer, primary_key=True)
    uid = Column(String(255), ForeignKey('vakt_policies.uid', ondelete='CASCADE'))
    subject = Column(Text())
    subject_regex = Column(String(2000))


class PolicyResourceModel(Base):
    """Storage model for policy resources"""

    __tablename__ = 'vakt_policy_resources'

    id = Column(Integer, primary_key=True)
    uid = Column(String(255), ForeignKey('vakt_policies.uid', ondelete='CASCADE'))
    resource = Column(Text())
    resource_regex = Column(String(2000))


class PolicyActionModel(Base):
    """Storage model for policy actions"""

    __tablename__ = 'vakt_policy_actions'

    id = Column(Integer, primary_key=True)
    uid = Column(String(255), ForeignKey('vakt_policies.uid', ondelete='CASCADE'))
    action = Column(Text())
    action_regex = Column(String(2000))


class PolicyModel(Base):
    """Storage model for policy"""

    __tablename__ = 'vakt_policies'

    uid = Column(String(255), primary_key=True)
    type = Column(SmallInteger)
    description = Column(Text())
    effect = Column(Boolean())
    context = Column(Text())
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
                      subjects=[self._policy_element_from_db(x.subject) for x in self.subjects],
                      resources=[self._policy_element_from_db(x.resource) for x in self.resources],
                      actions=[self._policy_element_from_db(x.action) for x in self.actions])

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
            PolicySubjectModel(subject=x, subject_regex=compiled) for (x, compiled)
            in cls._policy_elements_to_db(policy, policy_dict['subjects'])
        ]
        model.resources = [
            PolicyResourceModel(resource=x, resource_regex=compiled) for (x, compiled)
            in cls._policy_elements_to_db(policy, policy_dict['resources'])
        ]
        model.actions = [
            PolicyActionModel(action=x, action_regex=compiled) for (x, compiled)
            in cls._policy_elements_to_db(policy, policy_dict['actions'])
        ]
        return model

    @classmethod
    def _policy_elements_to_db(cls, policy, elements):
        for el in elements:
            value, compiled_value = None, None
            if policy.type == TYPE_STRING_BASED:
                value = el
                if policy.start_tag in el and policy.end_tag in el:
                    compiled_value = compile_regex(el, policy.start_tag, policy.end_tag).pattern
            else:  # it's a rule-based policy and it's value is a json
                value = json.dumps(el)
            yield (value, compiled_value)

    @classmethod
    def _policy_element_from_db(cls, element):
        try:
            return Rule.from_json(element)
        except:
            return element
