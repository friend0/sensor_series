#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="panopticon",
    # Don't forget to update src/pyocr/pyocr.py:VERSION as well
    # and download_url
    version="0.2.0",
    description=("A pure python OPC-XMLDA client implementation."),
    keywords="opc client kuka",
    url="https://bitbucket.com/teslarobotics/pyopc",
    #download_url="https://github.com/jflesch/pyocr/archive/v0.4.2.zip",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Treals",
        "License :: Proprietary AF",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: Robotics",
    ],
    license="Private Use Only - Tesla Motors 2016",
    author="Ryan Rodriguez",
    author_email="ryarodriguez@tesla.com",
    packages=find_packages(exclude=['docs', 'tests*']),
    data_files=[],
    scripts=[],
    install_requires=[],
)