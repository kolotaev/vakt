from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))
about = {}
with open(path.join(here, 'vakt', 'version.py'), mode='r', encoding='utf-8') as f:
    exec(f.read(), about)

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


if __name__ == '__main__':
    setup(
        name='vakt',
        description='Attribute-based access control (ABAC) SDK for Python',
        keywords='ACL ABAC access-control policy security authorization permission',
        version=about['__version__'],
        author='Egor Kolotaev',
        author_email='ekolotaev@gmail.com',
        license="Apache 2.0 license",
        url='http://github.com/kolotaev/vakt',
        long_description=long_description,
        long_description_content_type='text/markdown',
        py_modules=['vakt'],
        python_requires='>=3.6',
        install_requires=[
            'jsonpickle>=2.0',
        ],
        extras_require={
            'dev': [
                'pytest~=7.0',
                'pytest-cov~=4.0',
                'pylint~=2.13',
                'PyMySQL~=1.0',
                'psycopg2cffi~=2.8',
            ],
            'mongo': [
                'pymongo~=4.1',
            ],
            'sql': [
                'SQLAlchemy~=1.4',
            ],
            'redis': [
                'redis~=4.3'
            ],
        },
        packages=find_packages(exclude='tests'),
        classifiers=[
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Topic :: System :: Systems Administration',
            'Topic :: System :: Networking',
            'Topic :: System :: Networking :: Firewalls',
            'Topic :: Security',
            'Topic :: Software Development',
            'Topic :: Utilities',
            'Natural Language :: English',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
        ],
    )
