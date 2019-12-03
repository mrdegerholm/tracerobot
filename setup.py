#!/usr/bin/env python3
import setuptools

setuptools.setup(
    name="tracerobot",
    version="0.3.0",
    author="Markku Degerholm",
    author_email="markku.degerholm@knowit.fi",
    description="Python execution tracer with Robot Framework compatible output",
    packages=["tracerobot"],
    classifiers=["Programming Language :: Python :: 3"],
    install_requires=["robotframework>=3.1.1"]
)
