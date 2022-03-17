#!/usr/bin/env python
# encoding: utf-8
# pip install wheel
# python3 setup.py sdist bdist_wheel

from setuptools import setup

setup(name="forest_survival",
      version="0.1",
      description="game env for ai experimental",
      author="GongHuajun",
      author_email="earneet@gmail.com",
      packages=["forest_survival"],
      license="MIT License",
      python_requires=">=3.7",
      classifiers=[
          "Intended Audience :: Developers",
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "Topic :: Games/Entertainment",
          "Topic :: Multimedia :: Graphics",
          "Topic :: Software Development :: Libraries :: pygame"
      ])
