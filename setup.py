#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    include_package_data=True,
    name='limepress',
    version='0.2',
    author='Florian Scherf',
    url='https://github.com/limepress/limepress',
    author_email='mail@florianscherf.de',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'simple-logging-setup',
        'simple-plugin-manager',
        'rlpython',
        'jinja2>=2.10',
        'jinja2-simple-tags==0.4.0',
        'beautifulsoup4',
        'pyyaml~=6.0',
    ],
    scripts=[
        'bin/limepress',
        'bin/limepress-build',
        'bin/limepress-shell',
        'bin/limepress-dev-server',
    ],
)
