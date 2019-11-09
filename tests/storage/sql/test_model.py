import json
import uuid

from vakt.policy import Policy
from vakt.rules.operator import Eq
from vakt.rules.string import Equal
from vakt.storage.sql import PolicyModel, PolicySubjectModel, PolicyActionModel, PolicyResourceModel


def policy__model_assert(policy_model, policy):
    """
        Assert if the given policy model object `policy_model` is equal to the policy object `policy`
    """

    def element(el):
        if isinstance(el, dict):
            return json.dumps(el)
        elif isinstance(el, str):
            return el
        return None

    policy_json = policy.to_json()
    policy_dict = json.loads(policy_json)

    assert policy_model.uid == policy.uid
    assert policy_model.type == policy.type
    assert policy_model.description == policy.description

    assert len(policy_model.subjects) == len(policy.subjects)
    assert all(isinstance(policy_model.subjects[x], PolicySubjectModel) for x in range(len(policy_model.subjects)))
    assert all(policy_model.subjects[x].subject == element(policy_dict["subjects"][x]) for x in
               range(len(policy_model.subjects))) or \
           all(policy_model.subjects[x].subject_string == element(policy_dict["subjects"][x]) for x in
               range(len(policy_model.subjects)))

    assert len(policy_model.resources) == len(policy.resources)
    assert all(isinstance(policy_model.resources[x], PolicyResourceModel) for x in range(len(policy_model.resources)))
    assert all(policy_model.resources[x].resource == element(policy_dict["resources"][x]) for x in
               range(len(policy_model.resources))) or \
           all(policy_model.resources[x].resource_string == element(policy_dict["resources"][x]) for x in
               range(len(policy_model.resources)))

    assert len(policy_model.actions) == len(policy.actions)
    assert all(isinstance(policy_model.actions[x], PolicyActionModel) for x in range(len(policy_model.actions)))
    assert all(policy_model.actions[x].action == element(policy_dict["actions"][x]) for x in
               range(len(policy_model.actions))) or \
           all(policy_model.actions[x].action_string == element(policy_dict["actions"][x]) for x in
               range(len(policy_model.actions)))

    assert policy_model.context == json.dumps(policy_dict["context"])


class TestModel:

    def test_from_policy(self):
        id = str(uuid.uuid4())
        p = Policy(
            uid=id,
            description='foo bar баз',
            subjects=('Edward Rooney', 'Florence Sparrow'),
            actions=['<.*>'],
            resources=['<.*>'],
            context={
                'secret': Equal('i-am-a-teacher'),
            },
        )
        p_model = PolicyModel.from_policy(p)
        policy__model_assert(p_model, p)

    def test_update(self):
        id = str(uuid.uuid4())
        p = Policy(
            uid=id,
            description='foo bar баз',
            subjects=('Edward Rooney', 'Florence Sparrow'),
            actions=['<.*>'],
            resources=['<.*>'],
            context={
                'secret': Equal('i-am-a-teacher'),
            },
        )
        p_model = PolicyModel.from_policy(p)
        new_p = Policy(2, actions=[], subjects=[Eq('max'), Eq('bob')])
        p_model.update(new_p)
        policy__model_assert(p_model, new_p)

    def test_to_policy(self):
        id = str(uuid.uuid4())
        p = Policy(
            uid=id,
            description='foo bar баз',
            subjects=('Edward Rooney', 'Florence Sparrow'),
            actions=['<.*>'],
            resources=['<.*>'],
            context={
                'secret': Equal('i-am-a-teacher'),
            },
        )
        p_model = PolicyModel.from_policy(p)
        _p = p_model.to_policy()
        assert p.uid == _p.uid
        assert p.type == _p.type
        assert p.description == _p.description
        assert len(p.subjects) == len(_p.subjects)
        assert all(p.subjects[x] == _p.subjects[x] for x in range(len(p.subjects)))
        assert len(p.resources) == len(_p.resources)
        assert all(p.resources[x] == _p.resources[x] for x in range(len(p.resources)))
        assert len(p.actions) == len(_p.actions)
        assert all(p.actions[x] == _p.actions[x] for x in range(len(p.actions)))
        assert 'secret' in _p.context
        assert isinstance(_p.context['secret'], Equal)
        assert _p.context['secret'].val == 'i-am-a-teacher'
