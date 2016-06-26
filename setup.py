#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='selenium-chrome-screenshot',
    version='0.0.1',
    url='http://github.com/sanscore/selenium-chrome-screenshot/',

    description='',
    long_description='',
    keywords='selenium chrome screenshot',

    author='Grant Welch',
    author_email='gwelch925 at gmail.com',
    license='Apache License 2.0',

    packages=find_packages('src'),
    package_dir={'':'src'},

    install_requires=[
        'selenium',
        'Wand',
    ],

    setup_requires=[
    ],

    tests_require=[
    ],

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Session",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries",
    ],

    include_package_data=True,
    zip_safe=False,
)

