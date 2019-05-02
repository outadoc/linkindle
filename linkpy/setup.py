#!/usr/bin/env python3

from os import path
from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="linkpy",
    version="1.0",
    packages=['linkpy'],

    install_requires=['requests'],

    author="Baptiste Candellier",
    author_email="outadoc@gmail.com",
    description="This module allows you to retrieve your Linky consumption data "
                "from your Enedis account.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="GPLv3+",
    keywords="linky enedis edf erdf pylinky linkindle energy meter linkpy",
    url="https://github.com/outadoc/linkindle",
    project_urls={
        "Bug Tracker": "https://github.com/outadoc/linkindle/issues",
        "Source Code": "https://github.com/outadoc/linkindle",
    }
)
