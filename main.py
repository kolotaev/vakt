from inspect import signature

class A:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    @classmethod
    def foo(cls, data):
        inst = cls.__new__(cls)
        for k, v in data.items():
            setattr(inst, k, v)
        print('fff: ')
        print(len(signature(cls.__init__).parameters))

        return inst


name = 'A'
klass = globals()[name]
instance = klass.foo({'a': 12, 'b': 78})

print(instance)
print(instance.a)

