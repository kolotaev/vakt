import os
import logging

from vakt.managers.memory import MemoryManager
from vakt.rules.net import CIDRRule
from vakt.rules.string import StringEqualRule
from vakt.effects import DENY_ACCESS, ALLOW_ACCESS
from vakt.policy import DefaultPolicy
from vakt.matcher import RegexMatcher
from vakt.guard import Guard, Request

from flask import Flask, request, session

#          Set up vakt          #
# ============================= #


# First of all we need to create Policies for our book library.
# They can be added at any time via PolicyManager.
# Here comes the list of Policies:
policies = [
    DefaultPolicy(
        id='1',
        description="Allow everyone to log-in",
        effect=ALLOW_ACCESS,
        subjects=['<.*>'],
        resources=['<.*>'],
        actions=['login'],
    ),
    DefaultPolicy(
        id='2',
        description="""
        Allow all readers of the book library whose surnames start with M get and read any book or magazine,
        but only when they connect from local library's computer
        """,
        effect=ALLOW_ACCESS,
        subjects=['<[\w]+ M[\w]+>'],
        resources=('library:books:<.+>', 'office:magazines:<.+>'),
        actions=['<read|get>'],
        rules={
            'ip': CIDRRule('192.168.2.0/24'),
            # for local testing replace with CIDRRule('127.0.0.1'),
        },
    ),
    DefaultPolicy(
        id='3',
        description='Allow mr. Rooney and ms. Sparrow to do anything with the books',
        effect=ALLOW_ACCESS,
        subjects=('Edward Rooney', 'Florence Sparrow'),
        actions=['<.*>'],
        resources=['<.*>'],
        rules={
            'secret': StringEqualRule('i-am-a-teacher'),
        },
    ),
    DefaultPolicy(
        id='4',
        description='Disallow Ferris Bueller to do anything inside library. Even to log-in',
        effect=DENY_ACCESS,
        subjects=['Ferris Bueller'],
        actions=['<.*>'],
        resources=['<.*>'],
    ),
]

# Instantiate a global instance of Vakt guard.
# You can use local if you wish.
guard = None


def init():
    # Here we instantiate the Policy Manager.
    # In this case it's just in-memory one, but we can opt to SQL-storage Manager, MongoDB-storage Manager, etc.
    pm = MemoryManager()
    # And persist all our Policies so that to start serving our library.
    for p in policies:
        pm.create(p)
    # Create global guard instance
    global guard
    guard = Guard(pm, RegexMatcher())
    # Set up logger.
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(logging.StreamHandler())


#         Running server        #
# ============================= #

# Let's serve our book library
app = Flask(__name__)
Flask.secret_key = os.urandom(24)


@app.route('/')
def hello():
    return "Welcome to Online Book Library!"


@app.route('/login', methods=['POST'])
def login():
    user = request.form['name']
    vakt_request = Request(subject=user, action='login', context={'ip': request.remote_addr})
    if guard.is_allowed(vakt_request):
        # check password here
        session['fullname'] = user
        session['secret'] = request.form.get('secret', '')
        return "You've been logged-in", 200
    else:
        return "Go away, you violator!", 401


@app.route('/books/<action>/<book>')
def serve_book_request(action, book):
    vakt_request = Request(
        subject=session.get('fullname'),
        action=action,
        resource='library:books:%s' % book,
        context={
            'ip': request.remote_addr,
            'secret': session.get('secret', '')
        }
    )
    if guard.is_allowed(vakt_request):
        return "Enjoy! Here is the book you requested: '{}'!".format(book), 200
    else:
        return 'Sorry, but you are not allowed to do this!', 401


if __name__ == '__main__':
    init()
    app.run(debug=True)
