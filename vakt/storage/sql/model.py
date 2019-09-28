import json

from sqlalchemy import Column, Integer, SmallInteger, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from ...policy import Policy

Base = declarative_base()


class PolicySubjectModel(Base):
    """Storage model for policy subjects"""

    __tablename__ = 'policy_subject'

    id = Column(Integer, primary_key=True)
    uid = Column(String(254), ForeignKey('policy.uid', ondelete='CASCADE'))
    subject = Column(String(254))


class PolicyResourceModel(Base):
    """Storage model for policy resources"""

    __tablename__ = 'policy_resource'

    id = Column(Integer, primary_key=True)
    uid = Column(String(254), ForeignKey('policy.uid', ondelete='CASCADE'))
    resource = Column(String(254))


class PolicyActionModel(Base):
    """Storage model for policy actions"""

    __tablename__ = 'policy_action'

    id = Column(Integer, primary_key=True)
    uid = Column(String(254), ForeignKey('policy.uid', ondelete='CASCADE'))
    action = Column(String(254))


class PolicyModel(Base):
    """Storage model for policy"""

    __tablename__ = 'policy'

    uid = Column(String(254), primary_key=True)
    type = Column(SmallInteger)
    description = Column(String(254))
    effect = Column(String(254))
    context = Column(String(254))
    subjects = relationship(PolicySubjectModel, passive_deletes=True, lazy='joined')
    resources = relationship(PolicyResourceModel, passive_deletes=True, lazy='joined')
    actions = relationship(PolicyActionModel, passive_deletes=True, lazy='joined')

    @classmethod
    def from_policy(cls, policy):
        """
            Instantiate from policy object

            :param policy: object of type policy
        """
        policy_json = policy.to_json()
        policy_dict = json.loads(policy_json)
        rvalue = cls()
        rvalue.uid = policy_dict['uid']
        rvalue.type = policy_dict['type']
        rvalue.effect = policy_dict['effect']
        rvalue.description = policy_dict['description']
        rvalue.context = json.dumps(policy_dict['context'])
        rvalue.subjects = [PolicySubjectModel(subject=json.dumps(subject)) for subject in policy_dict['subjects']]
        rvalue.resources = [PolicyResourceModel(resource=json.dumps(resource)) for resource in policy_dict['resources']]
        rvalue.actions = [PolicyActionModel(action=json.dumps(action)) for action in policy_dict['actions']]
        return rvalue

    def update(self, policy):
        """
            Update object attributes to match given policy

            :param policy: object of type policy
        """
        policy_json = policy.to_json()
        policy_dict = json.loads(policy_json)
        self.uid = policy_dict['uid']
        self.type = policy_dict['type']
        self.effect = policy_dict['effect']
        self.description = policy_dict['description']
        self.context = json.dumps(policy_dict['context'])
        self.subjects = [PolicySubjectModel(subject=json.dumps(subject)) for subject in policy_dict['subjects']]
        self.resources = [PolicyResourceModel(resource=json.dumps(resource)) for resource in policy_dict['resources']]
        self.actions = [PolicyActionModel(action=json.dumps(action)) for action in policy_dict['actions']]

    def to_policy(self):
        """
            Create a policy object

            :return: object of type `Policy`
        """
        policy_dict = {
            "uid": self.uid,
            "effect": self.effect,
            "description": self.description,
            "context": json.loads(self.context),
            "subjects": [json.loads(x.subject) for x in self.subjects],
            "resources": [json.loads(x.resource) for x in self.resources],
            "actions": [json.loads(x.action) for x in self.actions]
        }
        policy_json = json.dumps(policy_dict)
        return Policy.from_json(policy_json)
