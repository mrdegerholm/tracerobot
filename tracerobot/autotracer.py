
#pylint: disable=too-many-instance-attributes,no-else-return,too-many-branches

import sys
import os
import tracerobot.utils

class AutoTracer:
    """ This class implements a python call tracer that can provides "keyword"
        log output to tracerobot logs. The output is enabled on a call depth
        range that starts from the test function itself (tracer is enabled
        much earlier than that) and ends to first method that looks like a
        private method or a system lib call. """

    def __init__(self, adapter, config):
        self._adapter = adapter
        self._trace_off_depth = 0
        self._log_on_depth = 0
        self._depth = 0
        self._kw = []
        self._is_exception = False
        self._kwtype = "kw"

        self._trace_privates = config['trace_privates'] if config else False
        self._trace_libpaths = [os.getcwd()]

        if 'trace_libpaths' in config:
            self._trace_libpaths += (config['trace_libpaths'] or [])

    def start(self):
        sys.settrace(self.trace)

    def stop(self):
        sys.settrace(None)

    def setkwtype(self, kwtype):
        self._kwtype = kwtype

    def debug(self, *args):
        #print("".ljust(self._depth), self._depth, ':', *args)
        pass

    def trace(self, frame, event, arg):

        if self._log_on_depth > 0 and self._depth < self._log_on_depth:
            self._log_on_depth = 0

        if event == "call":

            self._depth += 1

            if self._trace_off_depth > 0 and self._depth >= self._trace_off_depth:
                return self.trace

            name = frame.f_code.co_name
            file = frame.f_code.co_filename

            is_logged = self.is_func_logged(name, file)
            if is_logged:
                if not self._log_on_depth:
                    self._log_on_depth = self._depth
                    self.debug("Trace on at level ", self._log_on_depth)
                self._trace_off_depth = 0

            elif self._log_on_depth > 0:
                if not self._trace_off_depth:
                    self._trace_off_depth = self._depth
                    self.debug("Trace off at level ", self._trace_off_depth)

            if self._is_log_on():
                args = frame.f_locals
                args_str = ['{}={!r}'.format(k, v) for k, v in args.items()]
                self.debug(
                    "LOG", name, args,
                    self._depth, self._log_on_depth, self._trace_off_depth)
                kw = self._adapter.start_keyword(name, type=self._kwtype, args=args_str)
                self._kw.append(kw)
                self._kwtype = "kw"

            # Note: python docs say that the tracer function can return
            # an another tracer function instance here for the sub-scope
            # but it doesn't seem to be working like that in reality
            # (such sub-tracer was ignored when tried)
            return self.trace

        elif event == "exception":
            if self._is_log_on():
                (exception, value, tb) = arg
                msg = tracerobot.utils.format_exc(exception, value, tb)
                self.debug("exception", msg)
                self._adapter.end_keyword(self._kw.pop(), error_msg=msg)
                self._is_exception = True
            self._depth -= 1

        elif event == "return":
            if self._is_log_on() and not self._is_exception:
                self.debug("return", arg)
                self._adapter.end_keyword(self._kw.pop(), return_value=str(arg))

            if self._trace_off_depth > 0 and self._depth < self._trace_off_depth:
                self._trace_off_depth = 0

            self._is_exception = False
            self._depth -= 1

        return self.trace

    def is_func_logged(self, name, path):
        #self.debug("is_logged: ", path, name)
        if not self._trace_privates and name.startswith("_"):
            return False
        for libpath in self._trace_libpaths:
            if path.startswith(libpath):
                return True
        return False

    def _is_log_on(self):
        log_on = self._log_on_depth > 0 and self._depth >= self._log_on_depth
        trace_off = self._trace_off_depth > 0 and self._depth >= self._trace_off_depth
        return log_on and not trace_off
