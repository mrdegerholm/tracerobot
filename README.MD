# TraceRobot

## What is it?

TraceRobot is a Python-based test execution tracer. It outputs Robot Framework
compatible trace log (XML) of the instrumented tests. The generated XML log
can be then converted into a human-friendly log and report HTML pages.

TraceRobot module is meant to be used with pytest-tracerobot, which is a
plugin for the well-known Pytest framework. TraceRobot and pytest-tracerobot
are separate python modules for historical reasons, and will be probably
merged at some point.

So, in order to use TraceRobot, also check:
https://github.com/mrdegerholm/pytest-tracerobot

## Prerequisites

TraceRobot needs Python 3.6 or higher, PyPi (pip3) and Robot Framework installed.
TraceRobot is tested with Python 3.6.9 and Robot Framework 3.2b2.

## Installation

Extract the tarball or clone it from github. In the sources directory, run

sudo -H ./setup.py install

This should also install the Robot Framework using pip if necessary.

## Acknowledgements

Specials thanks go to Mica Nyholm and Ossi Rajuvaara for feedback and ideas!

I'm also thankful to Robot Framework and PyTest community for producing such
high-quality open-source products.
