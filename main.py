from functools import lru_cache
import re

counter = 0


@lru_cache(maxsize=512)
def get(key: str, foo: str, bar: str):
    global counter
    d = foo + key + bar
    counter = counter + 1
    return re.compile(d)

for m in range(3):
    for i in range(30):
        d = '//' + str(i) + '.*/'
        k = get(d, '<', '>')

print(get.cache_info())
print(counter)
