#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

from limepress import VERSION_STRING

setup(
    include_package_data=True,
    name='limepress',
    version=VERSION_STRING,
    author='Florian Scherf',
    url='',
    author_email='mail@florianscherf.de',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'lona',
    ],
    scripts=[],
)
