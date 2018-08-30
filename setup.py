from setuptools import setup, find_packages
from os import path

__version__ = '1.0.3'


with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


if __name__ == "__main__":
    setup(
        name='vakt',
        description='Attribute-based access control (ABAC) SDK for Python',
        keywords='ACL RBAC access policy security',
        version=__version__,
        author='Egor Kolotaev',
        author_email='ekolotaev@gmail.com',
        license="Apache 2.0 license",
        url='https://github.com/kolotaev/vakt',
        long_description=long_description,
        long_description_content_type='text/markdown',
        py_modules=['vakt'],
        install_requires=[],
        extras_require={
            'dev': [
                'pytest',
                'pytest-cov',
                'pylint',
            ]
        },
        packages=find_packages(exclude='tests'),
        classifiers=[
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: Implementation :: PyPy',
        ],
    )
