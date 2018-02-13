from setuptools import setup, find_packages

__version__ = '0.0.1'


with open('README.md') as f:
    README = f.read()


if __name__ == "__main__":
    setup(
        name='vakt',
        description='Python SDK for access policies',
        long_description=README,
        license="MIT license",
        version=__version__,
        author='Egor Kolotaev',
        author_email='ekolotaev@gmail.com',
        url='https://github.com/kolotaev/vakt',
        py_modules=['vakt'],
        install_requires=[],
        packages=find_packages(exclude='tests'),
        classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: PyPy',
        ],
    )
