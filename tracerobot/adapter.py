from robot.result.model import Message, Keyword, TestCase, TestSuite
from datetime import datetime

def timestamp():
    return datetime.now().strftime('%Y%m%d %H:%M:%S.%f')[0:-3]

class RobotAdapter:
    def __init__(self, writer):
        self.writer = writer
        self.parent_suite = None
        self._kw_stacks = []

    def start_suite(self, name, doc='', metadata=None, source=None):
        suite = TestSuite(
            name=name,
            doc=doc,
            metadata=metadata,
            source=source,
            starttime=timestamp()
        )

        suite.suites = []
        suite.tests = []

        if self.parent_suite:
            suite.parent = self.parent_suite
            self.parent_suite.suites.append(suite)

        self.parent_suite = suite
        self.writer.start_suite(suite)

        self._kw_stacks.append([])

        return suite

    def end_suite(self, suite, message=''):
        # NB: Suite status evaluated from tests automatically
        suite.endtime = timestamp()
        suite.message = message

        self.writer.end_suite(suite)
        self.parent_suite = suite.parent

        self._kw_stacks.pop()

    def start_test(self, name, doc='', tags=None):
        tags = tags or []

        test = TestCase(
            name=name,
            doc=doc,
            tags=tags,
            starttime=timestamp()
        )

        self._kw_stacks.append([])

        self.parent_suite.tests.append(test)
        self.writer.start_test(test)

        return test

    def end_test(self, test, error_msg=None):

        #HACK HACK HACK. Fixme properly...
        while len(self._kw_stacks[-1]): 
            kw = self._kw_stacks[-1][-1]
            self.end_keyword(kw)

        self._kw_stacks.pop()

        test.endtime = timestamp()

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

        if not self.parent_suite:
            return None

        keyword = Keyword(
            kwname=name,
            libname=libname,
            doc=doc,
            args=args,
            tags=tags,
            type=type,
            starttime=timestamp()
        )

        self.writer.start_keyword(keyword)

        self._kw_stacks[-1].append(keyword)

        return keyword

    def end_keyword(self, keyword, return_value=None, error_msg=None):

        if not keyword or not self.parent_suite:
            return

        keyword.endtime = timestamp()

        if not self._kw_stacks[-1]: 
            return

        kw = self._kw_stacks[-1].pop()

        assert kw is keyword
        if kw is not keyword:
            return

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
        if not level in ['NONE', 'FAIL', 'ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE']:
            return
        if self.parent_suite and self.parent_suite.tests and len(self._kw_stacks) and len(self._kw_stacks[-1]):
            self.writer.log_message(Message(msg, level))

    def get_writer(self):
        return self.writer
