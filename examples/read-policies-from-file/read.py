from vakt.reader import YamlReader
from vakt import MemoryStorage


storage = MemoryStorage()

policies = YamlReader('/path/to/file').read()
for p in policies:
    storage.add(p)

# Populates given storage with policies
YamlReader('/path/to/file', storage).populate()
