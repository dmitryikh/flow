import flow
from os.path import join, dirname
from setuptools import setup, find_packages
import sys

if sys.version_info < (3, 5):
    sys.exit('Sorry, Python < 3.5 is not supported')

setup(
    name='flow',
    version=flow.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md'), encoding='utf-8').read(),
    install_requires=[
        'graphviz==0.9',
    ],
    test_suite='flow.tests',
    tests_require=[
        'pytest',
    ],
)
