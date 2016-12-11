
from setuptools import setup, find_packages

setup(
    name="TestOPC",
    # Don't forget to update src/pyocr/pyocr.py:VERSION as well
    # and download_url
    version="0.2.0",
    description=("A pure python OPC-XMLDA client implementation."),
    keywords="opc client kuka",
    #url="https://bitbucket.com/",
    #download_url="https://github.com/jflesch/pyocr/archive/v0.4.2.zip",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Treals",
        "License :: Proprietary AF",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: Robotics",
    ],
    license="Not authorized for use.",
    author="Ryan Rodriguez",
    author_email="ryarodriguez@gmail.com",
    packages=find_packages(exclude=['docs', 'panopticon_tests*']),
    data_files=[],
    scripts=[],
    install_requires=[],
)