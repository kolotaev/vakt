import requests

#        Client requests        #
# ============================= #

host = 'http://127.0.0.1:5000'

r = requests.post(host + '/login', data={'name': 'Nina Martins', 'pass': 'my-password'})
assert 200 == r.status_code  # logged-in successfully
assert 200 == requests.get(host + '/books/get/Dracula', cookies=r.cookies).status_code  # allowed
assert 401 == requests.get(host + '/books/burn/Dracula', cookies=r.cookies).status_code  # not-allowed


r = requests.post(host + '/login', data={'name': 'Joe Jones', 'pass': 'my-password'})
assert 200 == r.status_code  # logged-in successfully
assert 401 == requests.get(host + '/books/get/Dracula', cookies=r.cookies).status_code  # not-allowed
assert 401 == requests.get(host + '/books/burn/Dracula', cookies=r.cookies).status_code  # not-allowed


# Ferris, go away!)
assert 401 == requests.post(host + '/login', data={'name': 'Ferris Bueller', 'pass': 'my-password'}).status_code


# Rooney can do everything in the school
r = requests.post(host + '/login',
                  data={'name': 'Edward Rooney', 'pass': 'my-password', 'secret': 'i-am-a-teacher'})
assert 200 == r.status_code  # logged-in successfully
assert 200 == requests.get(host + '/books/get/Dracula', cookies=r.cookies).status_code  # allowed
assert 200 == requests.get(host + '/books/burn/Dracula', cookies=r.cookies).status_code  # allowed


# suppose Sparrow doesn't know the secret phrase
r = requests.post(host + '/login',
                  data={'name': 'Florence Sparrow', 'pass': 'my-password', 'secret': 'i-do-not-know-the-secret'})
assert 200 == r.status_code  # logged-in successfully
assert 401 == requests.get(host + '/books/get/Dracula', cookies=r.cookies).status_code  # not-allowed
assert 401 == requests.get(host + '/books/burn/Dracula', cookies=r.cookies).status_code  # not-allowed

print('Everything works fine')
