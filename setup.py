#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="linkpy",
    version="0.5",
    packages=['linkpy'],

    install_requires=['requests', 'dateutil', 'json'],

    author="Baptiste Candellier",
    author_email="outadoc@gmail.com",
    description="This module allows you to retrieve your Linky consumption data from your Enedis account.",
    license="GPLv3+",
    keywords="linky enedis edf erdf pylinky linkindle energy meter",
    url="https://github.com/outadoc/linkindle",
    project_urls={
        "Bug Tracker": "https://github.com/outadoc/linkindle/issues",
        "Source Code": "https://github.com/outadoc/linkindle",
    }
)
