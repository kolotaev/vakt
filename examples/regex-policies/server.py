import os
import logging
import uuid

from vakt import (
    DENY_ACCESS, ALLOW_ACCESS, MemoryStorage,
    Policy, Guard, Inquiry, RegexChecker,
    rules,
)

from flask import Flask, request, session

from vakt.storage.mongo import MongoStorage
from pymongo import MongoClient

from vakt.storage.sql import SQLStorage
from vakt.storage.sql.model import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# ============================= #
#    Set up vakt and server     #
# ============================= #

# First of all we need to create Policies for our book library.
# They can be added at any time via Storage.
# Here comes the list of Policies:
policies = [
    Policy(
        uid=str(uuid.uuid4()),
        description="Allow everyone to log-in",
        effect=ALLOW_ACCESS,
        subjects=['<.*>'],
        resources=['<.*>'],
        actions=['login'],
    ),
    Policy(
        uid=str(uuid.uuid4()),
        description="""
        Allow all readers of the book library whose surnames start with M get and read any book or magazine,
        but only when they connect from local library's computer
        """,
        effect=ALLOW_ACCESS,
        subjects=[r'<[a-zA-Z]+ M[a-z]+>'],
        resources=('library:books:<.+>', 'office:magazines:<.+>'),
        actions=['<read|get>'],
        context={
            'ip': rules.CIDR('127.0.0.1/32'),
        },
    ),
    Policy(
        uid=str(uuid.uuid4()),
        description='Allow mr. Rooney and ms. Sparrow to do anything with the books',
        effect=ALLOW_ACCESS,
        subjects=('Edward Rooney', 'Florence Sparrow'),
        actions=['<.*>'],
        resources=['<.*>'],
        rules={
            'secret': rules.RegexMatch('[Ii]-am-a-teacher'),
        },
    ),
    Policy(
        uid=str(uuid.uuid4()),
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
    # Set up logger.
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(logging.StreamHandler())

    # Here we instantiate the Policy Storage.
    # We can opt to SQL, Memory or MongoDB Storage, any other third-party storage, etc.
    def create_sql_storage(dsn):
        engine = create_engine(dsn, echo=True)
        Base.metadata.create_all(engine)
        session = scoped_session(sessionmaker(bind=engine))
        return SQLStorage(scoped_session=session)
    use_storage = os.environ.get('STORAGE')
    print('storage is ', use_storage)
    if use_storage == 'mongo':
        user, password, host = 'root', 'example', 'localhost:27017'
        uri = 'mongodb://%s:%s@%s' % (user, password, host)
        st = MongoStorage(MongoClient(host=host), 'vakt_db', collection='vakt_book_library')
    elif use_storage == 'mysql':
        st = create_sql_storage('mysql+pymysql://root:root@localhost/vakt_db')
    elif use_storage == 'pg':
        st = create_sql_storage('postgresql+psycopg2://postgres:root@localhost/vakt_db')
    else:
        st = MemoryStorage()

    # And persist all our Policies so that to start serving our library.
    for p in policies:
        st.add(p)

    # Create global guard instance
    global guard
    guard = Guard(st, RegexChecker())


# ============================= #
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
    inquiry = Inquiry(subject=user, action='login', context={'ip': request.remote_addr})
    if guard.is_allowed(inquiry):
        # check password here
        session['fullname'] = user
        session['secret'] = request.form.get('secret', '')
        return "You've been logged-in", 200
    else:
        return "Go away, you violator!", 401


@app.route('/books/<action>/<book>')
def serve_book(action, book):
    inquiry = Inquiry(
        subject=session.get('fullname'),
        action=action,
        resource='library:books:%s' % book,
        context={
            'ip': request.remote_addr,
            'secret': session.get('secret', '')
        }
    )
    if guard.is_allowed(inquiry):
        return "Enjoy! Here is the book you requested: '{}'!".format(book), 200
    else:
        return 'Sorry, but you are not allowed to do this!', 401


if __name__ == '__main__':
    init()
    app.run(debug=True)
