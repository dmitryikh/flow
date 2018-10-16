from os.path import join, dirname
import rss_app
from setuptools import setup, find_packages
import sys

if sys.version_info < (3,5):
    sys.exit('Sorry, Python < 3.5 is not supported')

setup(
    name='rss_app',
    version=rss_app.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md'), encoding='utf-8').read(),
    entry_points={
        'console_scripts': [
            'rss_app = rss_app.main:main',
        ],
    },
    install_requires=[
        'flow==0.1.0',
        'feedparser==5.2.1',
        'sqlalchemy==1.1.18',
    ],
    test_suite='rss_app.tests',
    tests_require=[
        'pytest',
    ],
)
