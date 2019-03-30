import time

class RfwAdapter:

    def __init__(self, listener):
        self._listener = listener

    @staticmethod
    def _get_name(fun):
        in_module = hasattr(fun, '__module__')
        is_member = hasattr(fun, '__self__')

        name = (fun.__func__.__qualname__ if is_member
                else fun.__qualname__)

        if in_module:
            name = fun.__module__ + "." + name

        return name


    @staticmethod
    def _conv_instance(fun):
        if hasattr(fun, '__self__'):
            return [str(fun.__self__)]
        else:
            return []

    @staticmethod
    def _conv_args(args):
        return [repr(x) for x in args]

    @staticmethod
    def _conv_kwargs(kwargs):
        return [("%s=%s") % (repr(x), repr(y)) for x, y in kwargs.items()]

    @staticmethod
    def _to_time(t):
        utctime = time.gmtime(t)    # fixme localtime needed
        return time.strftime("%Y%m%d %H:%M:%S.", utctime) + str(int(t * 1000))


    def start_suite(self, suite_id, suite_name, doc=""):

        start = time.time()
        listener_args = {
            "id": suite_id,
            "name": suite_name,
            "doc": doc,
            "metadata": None,
            "source": None, #tbd
            "suites": None,       #tbd
            "tests": None,       #tbd
            "totaltests": 0,   #tbd
            "timeout": 0,   # tbd
            "starttime": self._to_time(start)
        }
        self._listener.start_suite(suite_id, listener_args)

        suite_info = {"listener_args": listener_args, "start": start}
        return suite_info

    def end_suite(self, suite_info, error_msg=None):

        listener_args = suite_info["listener_args"]
        suite_id = listener_args["id"]
        start = suite_info["start"]
        end = time.time()

        listener_args["endtime"] = self._to_time(end)
        listener_args["elapsedtime"] = str(int((end - start) * 1000))

        if error_msg:
            listener_args["status"] = "FAIL"
            listener_args["message"] = error_msg
        else:
            listener_args["status"] = "PASS"
            listener_args["message"] = ""

        self._listener.end_suite(suite_id, listener_args)


    def start_test(self, name, doc="", args="", is_critical=True, timeout=0):

        start = time.time()

        listener_args = {
            "id": name,
            "name": name,
            "args": args,
            "doc": doc,
            "tags": "",
            "critical": is_critical,
            "template": None,
            "starttime": self._to_time(start),
            "timeout": timeout
        }

        self._listener.start_test(name, listener_args)

        test_info = {"listener_args":  listener_args, "start_time": start}

        return test_info

    def start_test_fun(self, fun, args, kwargs, is_critical=True, timeout=0):

        name = self._get_name(fun)
        all_args = (
            self._conv_instance(fun) +
            self._conv_args(args) +
            self._conv_kwargs(kwargs))

        return self.start_test(name, fun.__doc__, all_args, is_critical, timeout)

    def end_test(self, test_info, error_msg=None):

        start = test_info["start_time"]
        end = time.time()

        listener_args = test_info["listener_args"]
        name = listener_args["name"]
        listener_args["endtime"] = self._to_time(end)
        listener_args["elapsedtime"] = str(int((end - start) * 1000))

        if error_msg:
            listener_args["status"] = "FAIL"
            listener_args["message"] = error_msg
        else:
            listener_args["status"] = "PASS"
            listener_args["message"] = ""

        self._listener.end_test(name, listener_args)

    def start_setup(self):
        self._listener.clear_test_count()

    def start_keyword(self, fun, args, kwargs):

        name = self._get_name(fun)

        all_args = (
            self._conv_instance(fun) +
            self._conv_args(args) +
            self._conv_kwargs(kwargs))

        kwtype = "kw"
        test_level = self._listener.get_test_level()
        if not test_level:
            kwtype = "setup" if not self._listener.get_test_count() else "teardown"

        start = time.time()

        listener_args = {
            "type": kwtype,
            "kwname": name,
            "libname": "",
            "doc": fun.__doc__,
            "args": all_args,
            "assign": None,
            "tags": [],
            "starttime": self._to_time(start),
            "timeout": 0 # tbd
        }

        self._listener.start_keyword(name, listener_args)

        kw_info = {"listener_args":  listener_args, "start_time": start}

        return kw_info

    def end_keyword(self, kw_info, return_value=None, error_msg=None):

        start = kw_info["start_time"]
        end = time.time()

        listener_args = kw_info["listener_args"]
        name = listener_args["kwname"]
        listener_args["endtime"] = self._to_time(end)
        listener_args["elapsedtime"] = str(int((end - start) * 1000))

        if error_msg:
            listener_args["status"] = "FAIL"
            listener_args["message"] = error_msg
            self._listener.log_message(error_msg)
        else:
            listener_args["status"] = "PASS"
            listener_args["message"] = ""
            self._listener.log_message("Return: " + str(return_value))

        self._listener.end_keyword(name, listener_args)
