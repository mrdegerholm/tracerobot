import time
from collections import defaultdict
from datetime import datetime

from robot.result.model import Message, Keyword, TestCase, TestSuite
from tracerobot import utils


class RobotAdapter:
    def __init__(self, writer):
        self.writer = writer
        self.parent_suite = None

    def start_suite(self, name, doc='', metadata=None, source=None):
        suite = TestSuite(
            name=name,
            doc=doc,
            metadata=metadata,
            source=source,
            starttime=utils.timestamp()
        )

        suite.suites = []
        suite.tests = []

        if self.parent_suite:
            suite.parent = self.parent_suite
            self.parent_suite.suites.append(suite)

        self.parent_suite = suite
        self.writer.start_suite(suite)

        return suite

    def end_suite(self, suite, message=''):
        # NB: Suite status evaluated from tests automatically
        suite.endtime = utils.timestamp()
        suite.message = message

        self.writer.end_suite(suite)
        self.parent_suite = suite.parent

    def start_test(self, name, doc='', tags=None):
        tags = tags or []

        test = TestCase(
            name=name,
            doc=doc,
            tags=tags,
            starttime=utils.timestamp()
        )

        self.parent_suite.tests.append(test)
        self.writer.start_test(test)

        return test

    def end_test(self, test, error_msg=None):
        test.endtime = utils.timestamp()

        if error_msg:
            test.status = 'FAIL'
            test.message = error_msg
        else:
            test.status = 'PASS'

        self.writer.end_test(test)

    def start_keyword(self, name, type='kw', libname='', doc='', args=None,
                      tags=None):
        args = args or []
        tags = tags or []

        keyword = Keyword(
            kwname=name,
            libname=libname,
            doc=doc,
            args=args,
            tags=tags,
            type=type,
            starttime=utils.timestamp()
        )

        self.writer.start_keyword(keyword)

        return keyword

    def end_keyword(self, keyword, return_value=None, error_msg=None):
        keyword.endtime = utils.timestamp()

        if error_msg:
            keyword.status = 'FAIL'
            keyword.message = error_msg
            self.log_message(error_msg)
        else:
            keyword.status = 'PASS'
            self.log_message('Return: ' + str(return_value))

        self.writer.end_keyword(keyword)

    def log_message(self, msg, level='INFO'):
        self.writer.log_message(Message(msg, level))
