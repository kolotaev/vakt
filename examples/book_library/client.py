import requests

#        Client requests        #
# ============================= #

r = requests.post('http://library.online/login', data={'name': 'Nina Martins', 'pass': 'my-password'})
requests.get('http://library.online/books/get/Dracula', cookies=r.cookies)  # allowed
requests.get('http://library.online/books/burn/Dracula', cookies=r.cookies)  # not-allowed


r = requests.post('http://library.online/login', data={'name': 'Joe Jones', 'pass': 'my-password'})
requests.get('http://library.online/books/get/Dracula', cookies=r.cookies)  # not-allowed
requests.get('http://library.online/books/burn/Dracula', cookies=r.cookies)  # not-allowed


# Ferris, go away!)
requests.post('http://library.online/login', data={'name': 'Ferris Bueller', 'pass': 'my-password'})


r = requests.post('http://library.online/login',
                  data={'name': 'Edward Rooney', 'pass': 'my-password', 'secret': 'i-am-a-teacher'})
requests.get('http://library.online/books/get/Dracula', cookies=r.cookies)  # allowed
requests.get('http://library.online/books/burn/Dracula', cookies=r.cookies)  # allowed


# suppose Sparrow doesn't know the secret phrase
r = requests.post('http://library.online/login',
                  data={'name': 'Florence Sparrow', 'pass': 'my-password', 'secret': 'i-do-not-know-the-secret'})
requests.get('http://library.online/books/get/Dracula', cookies=r.cookies)  # not-allowed
requests.get('http://library.online/books/burn/Dracula', cookies=r.cookies)  # not-allowed
