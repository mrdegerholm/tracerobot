from robot.result.model import Message, Keyword, TestCase, TestSuite
from tracerobot import utils
from tracerobot import autotracer


class RobotAdapter:
    def __init__(self, writer, autotracer_cfg=None):
        self.writer = writer
        self.parent_suite = None
        self.tracer = None
        self._kwlevel = 0
        self._autotracer_cfg = autotracer_cfg

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

        self._kwlevel = 0

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

        if not self.parent_suite or not self.parent_suite.tests:
            return None

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

        self._kwlevel += 1

        return keyword

    def end_keyword(self, keyword, return_value=None, error_msg=None):

        if not keyword or not self.parent_suite or not self.parent_suite.tests:
            return

        keyword.endtime = utils.timestamp()

        self._kwlevel -= 1
        assert self._kwlevel >= 0

        if error_msg:
            keyword.status = 'FAIL'
            keyword.message = error_msg
            self.log_message(error_msg)
        else:
            keyword.status = 'PASS'
            if return_value is not None:
                self.log_message('Return: ' + str(return_value))

        self.writer.end_keyword(keyword)

    def log_message(self, msg, level='INFO'):
        if self.parent_suite and self.parent_suite.tests and self._kwlevel:
            self.writer.log_message(Message(msg, level))

    def start_auto_trace(self):
        self.tracer = autotracer.AutoTracer(self, self._autotracer_cfg)
        self.tracer.start()

    def stop_auto_trace(self):
        if self.tracer:
            self.tracer.stop()
        self.tracer = None

    def set_auto_trace_kwtype(self, kwtype):
        if self.tracer:
            self.tracer.setkwtype(kwtype)

    def get_writer(self):
        return self.writer
