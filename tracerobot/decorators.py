from functools import wraps

import tracerobot
from tracerobot import utils


def format_exc(exc):
    if isinstance(exc, AssertionError):
        return ','.join(str(a) for a in exc.args)
    else:
        return repr(exc)


def decorator(dec):
    """Decorator to convert a function into a decorator."""
    @wraps(dec)
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            return dec(func, *args, **kwargs)
        return inner
    return outer


@decorator
def suite(func, *args, **kwargs):
    msg = None
    name = func.__qualname__
    doc = func.__doc__
    info = tracerobot.start_suite(name, name, doc)

    try:
        return func(*args, **kwargs)
    except Exception as e:
        msg = format_exc(e)
        raise
    finally:
        tracerobot.end_suite(info, msg)


@decorator
def testcase(func, *args, **kwargs):
    msg = None
    info = tracerobot.start_test_func(func, args, kwargs)

    try:
        return func(*args, **kwargs)
    except Exception as e:
        msg = format_exc(e)
        raise
    finally:
        tracerobot.end_test(info, msg)


@decorator
def keyword(func, *args, **kwargs):
    ret, msg = None, None

    name = utils.function_name(func)
    doc = func.__doc__
    args_fmt = utils.format_args(args, kwargs)

    info = tracerobot.start_keyword(name=name, doc=doc, args=args_fmt)

    try:
        ret = func(*args, **kwargs)
    except Exception as e:
        msg = format_exc(e)
        raise
    finally:
        tracerobot.end_keyword(info, ret, msg)

    return ret


class ClassInitLogger(type):
    """Allows logging of class instantiations, i.e. calls to __init__()"""
    def __new__(mcs, name, bases, dct):
        instance = super().__new__(mcs, name, bases, dct)
        instance.__init__ = keyword(instance.__init__)
        return instance


class KeywordClass(metaclass=ClassInitLogger):
    """Automatically decorates all non-private member functions as @keyword.
    Note: this also decorates all non-private sub-classes.
    """
    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if callable(attr) and not attr.__name__.startswith('_'):
            return keyword(attr)
        else:
            return attr
