import Pyro4
from vakt import Inquiry

Pyro4.config.SERIALIZER = 'pickle'

gh = Pyro4.Proxy('PYRO:github.guardian@localhost:9999')


# regular user tries to access Google repositories
assert gh.check(Inquiry(action='get', resource='repos/google/tensorflow', subject='Max'))
assert gh.check(Inquiry(action='list', resource='repos/google/tensors-ui', subject='Jimmy'))
assert not gh.check(Inquiry(action='list', resource='repos/google/clusterfuzz', subject='Jimmy'))


# deletion requests
assert not gh.check(Inquiry(action='delete', resource='repos/facebook/react', subject='Max'))
assert not gh.check(Inquiry(action='exterminate', resource='repos/facebook/react', subject={'name': 'Max'}))
assert gh.check(Inquiry(action='delete', resource='repos/facebook/react', subject='defunkt'))
assert gh.check(Inquiry(action='prune', resource='repos/facebook/php', subject={'name': 'defunkt'}))
assert gh.check(Inquiry(action='prune', resource='repos/google/', subject={'name': 'defunkt', 'role': 'non-admin'}))
assert gh.check(Inquiry(action='delete', resource='repos/facebook/ui', subject={'name': 'Jim', 'role': 'admin'}))


# administration panel requests
assert not gh.check(Inquiry(action='maintenance',
                            resource={'category': 'administration', 'sub': 'panel'},
                            subject={'name': 'Jim'},
                            context={'ip': '175.8.20.1'}))
assert not gh.check(Inquiry(action='put-on-fire',
                            resource={'category': 'administration', 'sub': 'switch'},
                            subject={'name': 'Jim', 'role': 'developer'},
                            context={'ip': '127.0.0.1'}))
assert gh.check(Inquiry(action='off',
                        resource={'category': 'administration', 'sub': 'switch'},
                        subject={'name': 'Jim', 'role': 'admin'},
                        context={'ip': '127.0.0.1'}))
assert not gh.check(Inquiry(action='off',
                            resource={'category': 'administration', 'sub': 'switch'},
                            subject={'name': 'Jim', 'role': 'admin'},
                            context={'ip': '175.8.20.1'}))
assert not gh.check(Inquiry(action='off',
                            resource={'category': 'administration', 'sub': 'protected'},
                            subject={'name': 'Jim', 'role': 'admin'},
                            context={'ip': '127.0.0.1'}))


# repo fork requests
assert not gh.check(Inquiry(action='fork', resource='repos/datadog/kafka-kit', subject={'name': 'Jim', 'stars': 1}))
assert gh.check(Inquiry(action='fork', resource='repos/DataDog/kafka-kit', subject={'name': 'Ho', 'stars': 80}))
assert gh.check(Inquiry(action='fork', resource='repos/DataDog/consul', subject={'name': 'Ho', 'stars': 998}))
assert gh.check(Inquiry(action='fork', resource='repos/datadog/consul', subject={'name': 'Ho', 'stars': 998}))
assert not gh.check(Inquiry(action='fork', resource='repos/DataDog/consul', subject={'name': 'Ho', 'stars': 999}))


print('Everything works fine')
