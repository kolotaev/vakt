from yaml import load, dump, Loader, Dumper


def test_example_yaml():
    with open('vakt/examples/read-policies-from-file/policies.yaml', 'r') as f:
        data = load(f, Loader=Loader)
        assert data
