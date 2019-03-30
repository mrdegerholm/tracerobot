from tracerobot.rt_state import RtState

def suite(fun):
    def decorator():
        adapter = RtState.get_adapter()

        name = fun.__qualname__
        doc = fun.__doc__
        suite_info = adapter.start_suite(name, name, doc)

        try:
            fun()

        except Exception as e:
            msg = repr(e)
            adapter.end_suite(suite_info, msg)
            raise

        adapter.end_suite(suite_info)

    return decorator

def testcase(fun):
    def decorator(*args, **kwargs):
        adapter = RtState.get_adapter()

        test_info = adapter.start_test_fun(fun, args, kwargs)

        try:
            fun(*args, **kwargs)

        except AssertionError as e:
            msg = str(e.args) if len(e.args) > 1 else str(e.args[0])
            adapter.end_test(test_info, msg)
            raise
        except Exception as e:
            msg = repr(e)
            adapter.end_test(test_info, msg)
            raise

        adapter.end_test(test_info)

    return decorator

def keyword(fun):
    def decorator(*args, **kwargs):
        adapter = RtState.get_adapter()

        kw_info = adapter.start_keyword(fun, args, kwargs)

        try:
            ret = fun(*args, **kwargs)

        except AssertionError as e:
            msg = str(e.args) if len(e.args) > 1 else str(e.args[0])
            adapter.end_keyword(kw_info, None, msg)
            raise
        except Exception as e:
            msg = repr(e)
            adapter.end_keyword(kw_info, None, msg)
            raise

        adapter.end_keyword(kw_info, ret)

        return ret

    return decorator

class ClassInitLogger(type):
    """ Allows logging of  class instantiations i.e. calls to __init__() """
    def __new__(mcs, name, bases, dct):
        instance = super().__new__(mcs, name, bases, dct)
        instance.__init__ = keyword(instance.__init__)
        return instance


class KeywordClass(metaclass=ClassInitLogger):
    """ Automatically decorates all non-private member functions as @keyword.
        Note: this also decorates all non-private sub-classes. """
    def __getattribute__(self, attr):
        v = super().__getattribute__(attr)
        if callable(v) and not v.__name__.startswith("_"):
            return keyword(v)
        else:
            return v
