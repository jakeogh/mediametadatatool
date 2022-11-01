# -*- coding: utf-8 -*-

import fastentrypoints
from setuptools import find_packages, setup

dependencies = ["click"]

config = {
    "version": "0.1",
    "name": "mediametadatatool",
    "url": "https://github.com/jakeogh/mediametadatatool",
    "license": "ISC",
    "author": "Justin Keogh",
    "author_email": "github.com@v6y.net",
    "description": "extract metadata from media",
    "long_description": __doc__,
    "packages": find_packages(exclude=['tests']),
    "package_data": {"mediametadatatool": ['py.typed']},
    "include_package_data": True,
    "zip_safe": False,
    "platforms": "any",
    "install_requires": dependencies,
    "entry_points": {
        "console_scripts": [
            "mediametadatatool=mediametadatatool.mediametadatatool:cli",
        ],
    },
}

setup(**config)