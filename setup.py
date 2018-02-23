from setuptools import setup, find_packages
import os
import inspect

__version__ = '0.0.1'


with open('README.md') as f:
    README = f.read()


__location__ = os.path.join(os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe())))
install_reqs = [req for req in
                open(os.path.join(__location__, 'requirements.txt')).read().split('\\n')
                if req != '']


if __name__ == "__main__":
    setup(
        name='vakt',
        description='Python SDK for access policies',
        long_description=README,
        keywords=(),
        version=__version__,
        author='Egor Kolotaev',
        author_email='ekolotaev@gmail.com',
        license="MIT license",
        url='https://github.com/kolotaev/vakt',
        py_modules=['vakt'],
        install_requires=install_reqs,
        tests_require=['pytest'],
        packages=find_packages(exclude='tests'),
        classifiers=[
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: Implementation :: PyPy',
        ],
    )
