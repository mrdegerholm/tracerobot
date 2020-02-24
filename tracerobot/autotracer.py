
#pylint: disable=too-many-instance-attributes,no-else-return,too-many-branches

import sys
import os
import tracerobot.utils
import traceback

class AutoTracer:
    """ This class implements a python call tracer that can provides "keyword"
        log output to tracerobot logs. The output is enabled on a call depth
        range that starts from the test function itself (tracer is enabled
        much earlier than that) and ends to first method that looks like a
        private method or a system lib call. """

    def __init__(self, adapter, config):
        self._adapter = adapter
        self._depth = 0
        self._ctx = []
        self._kwtype = "kw"
        self._is_exc_handled = False

        self._trace_privates = config['trace_privates'] if config else False
        self._trace_libpaths = [os.getcwd()]
        self._trace_silentpaths = []

        if 'trace_libpaths' in config:
            self._trace_libpaths += (config['trace_libpaths'] or [])

        if 'trace_silentpaths' in config:
            self._trace_silentpaths += (config['trace_silentpaths'] or [])

    def start(self):
        self._ctx = []
        sys.settrace(self.trace)

    def stop(self):
        sys.settrace(None)

    def setkwtype(self, kwtype):
        self._kwtype = kwtype

    class DummyCtx:
        def __init__(self):
            pass

        def handle_exc(self, arg, is_original):
            pass

        def finish(self, arg):
            pass

        def is_in_scope(self):
            return False


    class TraceCtx:

        @staticmethod
        def _format_arg(args, locals, i):
            arg = args[i]
            value = locals[arg]
            return '{}={!r}'.format(arg, value)

        def __init__(self, tracer, kwtype, frame, in_scope, is_external):
            self._tracer = tracer
            self._depth = tracer._depth
            self._kwtype = kwtype
            self._is_in_scope = in_scope

            self._kw = None
            self._name = frame.f_code.co_name

            args = frame.f_code.co_varnames
            locals = frame.f_locals

            args_str = [ self._format_arg(args, locals, i) for i in range(frame.f_code.co_argcount)]

            self.debug("LOG", self._kwtype, args_str)
            name = self._name if not is_external else (
                frame.f_code.co_filename + ":" +
                str(frame.f_code.co_firstlineno) + ":" +
                self._name)
            self._kw = self._tracer._adapter.start_keyword(
                name, type=self._kwtype, args=args_str)

        def handle_exc(self, arg, is_original):
            (exception, value, tb) = arg
            (exc_source, msg) = tracerobot.utils.format_exc(exception, value, tb)

            self.debug("EXC", msg)

            if is_original:
                exc_kw = tracerobot.start_keyword(exc_source)
                tracerobot.end_keyword(exc_kw, error_msg=msg)

            self._tracer._adapter.end_keyword(self._kw, error_msg=msg)
            self._kw = None

        def finish(self, arg):
            self.debug("RET")
            if self._kw:
                self._tracer._adapter.end_keyword(self._kw, return_value=str(arg))

        def is_in_scope(self):
            return self._is_in_scope

        def debug(self, *args):
            if False:   # Set to True to enable tracer debugging
                sys.settrace(None)
                depth = self._tracer._depth
                print("".ljust(depth), depth, ":", self._name, ":", *args)
                sys.settrace(self._tracer.trace)

    def trace(self, frame, event, arg):

        if event == "call":

            self._depth += 1

            name = frame.f_code.co_name
            path = frame.f_code.co_filename

            (in_scope, is_external, is_silent) = self.is_func_logged(name, path)
            if not is_silent and (in_scope or self.is_log_children()):
                ctx = AutoTracer.TraceCtx(
                        self, self._kwtype, frame, in_scope, is_external)
                self._kwtype = "kw"
            else:
                ctx = AutoTracer.DummyCtx()

            self._ctx.append(ctx)

            self._is_exc_handled = False

        elif event == "exception":
            self._ctx[-1].handle_exc(arg, not self._is_exc_handled)
            self._is_exc_handled = True
            # for exceptions, exception event is handled first and then
            # return event

        elif event == "return":
            self._ctx[-1].finish(arg)
            self._ctx.pop()
            self._depth -= 1

        assert self._depth >= 0

        # Note: python docs say that the tracer function can return
        # an another tracer function instance here for the sub-scope
        # but it doesn't seem to be working like that in reality
        # (such sub-tracer was ignored when tried)

        return self.trace

    def is_func_logged(self, name, path):
        """ Returns tuple (in_scope, is_external, is_silent) """

        for libpath in self._trace_silentpaths:
            if path.startswith(libpath):
                return (False, False, True)

        if not self._trace_privates and name.startswith("_"):
            return (False, False, False)

        for libpath in self._trace_libpaths:
            if path.startswith(libpath):
                return (True, False, False)

        return (False, True, False)

    def is_log_children(self):
        return self._ctx and self._ctx[-1].is_in_scope()
