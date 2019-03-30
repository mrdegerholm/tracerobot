# TraceRobot

## What is it?

TraceRobot is a Python-based test execution tracer. It outputs Robot Framework
compatible trace log (XML) of the instrumented tests. The generated XML log
can be then converted into a human-friendly log and report HTML pages.

TraceRobot module is not especially useful alone. It is intended to be used
with some testing framework such as PyTest. In fact, there is a distinct
PyTest plugin module called pytest-tracerobot that starts to make things interesting.
WIth PyTest, pytest-tracerobot and the this module, you can get a
test execution trace with a minimal amount of additional instrumentation.

## Current status

Current development status is Alpha / PoC phase.
I'm looking for volunteers to assist in development of TraceRobot.

## Prerequisites

TraceRobot needs Python 3, PyPi (pip3) and Robot Framework installed.
TraceRobot is tested with Python 3.5.2 and Robot Framework 3.1.1.

## Installation

Extract the tarball or clone it from github. In the sources directory, run

sudo -H ./setup.py install

This should also install the Robot Framework using pip if necessary.

## Running the example code

After installing the module, you can run the example code under the "example"
directory.

The example code comprises of a SUT (Software Under Testing), and a few
test cases for that. The SUT is a very simple HTTP API stub.

First, run the SUT (Software Under testing) in one terminal:

`./gameserver.py`

Then, open an another terminal for running the tests:

`./run.sh`

This script runs both the tests and calls 'rebot' tool from Robot framework
to generate report.html and log.html from the generated output.xml.

If all goes well, you can use your favorite browser to open the report
and/or log documents.

## Writing test suites, test cases and keywords

Based on Robot Framework testing model, TraceRobot inherits the following
basic concepts:
  1 Suite: a collection of tests. There can be one or multiple suites per test run,
    and suites can be nested.
    Suites can have setup and teardown related keywords.
  1 Test case: a single test case. Test cases cannot be nested.
    Test cases can have setup and teardown related keywords.
  1 Keyword: basically any Python function used by a test case. Keywords can
    call other keywords.

TraceRobot module provides a three-level API to assist in instrumenting the
test code:

  1 The low-level API in rfw_adapter.py with calls to start and end
    suites, test cases and keywords.
  2 Decorators API in decorators.py that can be used to log a Python function
    call as a suite, test case or keyword.
  3 Base classes in decorators.py that can be used to automatically instrument
    all public methods in your test classes as keywords.

The following decorators are supported:

@suite: the decorated function executes a set of tests.

@testcase: the decorated function is a test case.

@keyword: the decorated function is a keyword. Arguments and return values are logged.


## What is missing

Logging of the following things supported by Robot Framework logs are not
currently supported:
   - Tags
   - "is_critical"
   - timeouts

The underlying test framework may still provide such features, they just don't
get logged (yet). Contributions welcome!

## Acknowledgements

Specials thanks go to Mica Nyholm and Ossi Rajuvaara for feedback and ideas!

I'm also thankful to Robot Framework and PyTest community for producing such
high-quality open-source products.
