from setuptools import setup

__version__ = '0.0.1'

if __name__ == "__main__":
    setup(
        name='vakt',
        description='Python SDK for access policies',
        long_description=open("README.md").read(),
        license="MIT license",
        version=__version__,
        author='Egor Kolotaev',
        author_email='ekolotaev@gmail.com',
        url='https://github.com/kolotaev/vakt',
        py_modules=['vakt'],
        install_requires=['pytest>=3.3.1'],
        tests_require=['pytest>=3.3.1'],
        classifiers=[
            'Framework :: Pytest',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
        ],
    )
