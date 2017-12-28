from functools import lru_cache
import re


@lru_cache(maxsize=512)
def get(key):
    return re.compile(key)

for m in range(4):
    for i in range(30):
        d = '//' + str(i) + '.*/'
        k = get(d)

print(get.cache_info())
