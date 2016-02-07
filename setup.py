# -*- coding: utf-8 -*-
"""
Setuptools script for testing-aids (testing.aid)

"""
from setuptools import setup, find_packages

Name = 'testing-aid'
ProjectUrl = ""
Version = "1.0.3"
Author = ''
AuthorEmail = ''
Maintainer = ''
Summary = 'Helpers for running docker containers as fixtures under py.test.'
License = ''
Description = Summary
ShortDescription = Summary

needed = [
    'schematics==1.1.0',
    'pyyaml',
    'pytest',
    'requests',
    # This is required but it insists on a requests version <2.5.0 which
    # conflicts with other libraries I've no control over.
    #'docker-py',
    'ipdb',
    'selenium',
]

import platform

if platform.system() in ['Linux', 'Darwin']:
    # Used with selenium webdriver for headless testing.
    needed.append('pyvirtualdisplay')


test_needed = [
]

test_suite = 'testing.aid.tests'

EagerResources = [
    'testing',
]

ProjectScripts = [
]

PackageData = {
    '': ['*.*'],
}

EntryPoints = """
"""

setup(
    url=ProjectUrl,
    name=Name,
    zip_safe=False,
    version=Version,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=Description,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
    ],
    keywords='web pytest',
    license=License,
    scripts=ProjectScripts,
    install_requires=needed,
    tests_require=test_needed,
    test_suite=test_suite,
    include_package_data=True,
    packages=find_packages(),
    package_data=PackageData,
    eager_resources=EagerResources,
    entry_points=EntryPoints,
    namespace_packages=[u'testing'],
)
