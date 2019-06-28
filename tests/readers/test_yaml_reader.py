from yaml import load, load_all, Loader


def test_example_yaml():
    with open('vakt/examples/read-policies-from-file/policies.yaml', 'r') as f:
        # use load-all for multi-documents
        data = load_all(f, Loader=Loader)
        assert data
