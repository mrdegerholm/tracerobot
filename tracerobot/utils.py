from contextlib import contextmanager
from datetime import datetime
import traceback


@contextmanager
def catch_exc():
    try:
        yield
    except Exception as exc:
        print(exc)


def function_name(func):
    in_module = hasattr(func, '__module__')
    is_member = hasattr(func, '__self__')

    if is_member:
        name = func.__func__.__qualname__
    else:
        name = func.__qualname__

    if in_module:
        name = func.__module__ + '.' + name

    return name


def instance(func):
    if hasattr(func, '__self__'):
        return [str(func.__self__)]
    else:
        return []


def timestamp():
    # TODO: Can probably be replaced with robot in-built utils
    return datetime.now().strftime('%Y%m%d %H:%M:%S.%f')[0:-3]


def format_args(*args, **kwargs):
    return ([repr(a) for a in args] +
            ['{!r}={!r}'.format(k, v) for k, v in kwargs.items()])

def format_exc(exc, value, tb):
    stack_summary = traceback.extract_tb(tb)
    frames = traceback.format_list(stack_summary)
    #msg = frames[-1] + "\n" + call.excinfo.exconly()
    msg = str(frames[-1]) + "\n" + str(traceback.format_exception_only(exc, value))
    return msg
