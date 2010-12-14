#! /usr/bin/env python

# Copyright (C) 2010 Antti Kaihola
# E-mail: akaihol PLUS python AT ambitone DOT com

import os


NAME = 'eyam'
MODULES = ['eyam']
DESCRIPTION = 'A Python Mocking Isolation Library for Testing'

URL = "http://github.com/akaihola/eyam/"

readme = os.path.join(os.path.dirname(__file__), 'README.txt')
LONG_DESCRIPTION = open(readme).read()

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Testing',
]

AUTHOR = 'Antti Kaihola'
AUTHOR_EMAIL = 'akaihol+python@ambitone.com'
KEYWORDS = ("testing test mock mocking unittest patching "
            "stubs fakes doubles").split(' ')

params = dict(
    name=NAME,
    version='0.1',
    py_modules=MODULES,

    # metadata for upload to PyPI
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    keywords=KEYWORDS,
    url=URL,
    classifiers=CLASSIFIERS,
)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
else:
    params['tests_require'] = ['unittest2', 'mock']
    params['test_suite'] = 'unittest2.collector'

setup(**params)
