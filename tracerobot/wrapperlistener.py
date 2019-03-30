# utf-8

import robot.model.message

def to_obj(attrs):
    class X:
        pass

    x = X()
    x.__dict__.update(attrs)

    return x


class WrapperListener:

    def __init__(self, wrapped):
        self._wrapped = wrapped
        self._suiteLevel = 0
        self._testLevel = 0
        self._testCount = 0

    def get_suite_level(self):
        return self._suiteLevel

    def get_test_level(self):
        return self._testLevel

    def get_test_count(self):
        return self._testCount

    def clear_test_count(self):
        self._testCount = 0

    def start_suite(self, name, attrs):
        self._suiteLevel += 1
        self._testCount = 0
        try:
            self._wrapped.start_suite(to_obj(attrs))
        except Exception as e:
            print(repr(e))
            raise e

    def end_suite(self, name, attrs):
        self._suiteLevel -= 1
        try:
            self._wrapped.end_suite(to_obj(attrs))
        except Exception as e:
            print(repr(e))
            raise e

    def start_test(self, name, attrs):
        if not self._suiteLevel:
            return
        self._testLevel += 1
        self._testCount += 1
        try:
            self._wrapped.start_test(to_obj(attrs))
        except Exception as e:
            print(repr(e))
            raise e

    def end_test(self, name, attrs):
        if not self._suiteLevel:
            return
        self._testLevel -= 1
        try:
            self._wrapped.end_test(to_obj(attrs))
        except Exception as e:
            print(repr(e))
            raise e

    def start_keyword(self, name, attrs):
        if not self._suiteLevel:
            return
        try:
            self._wrapped.start_keyword(to_obj(attrs))
        except Exception as e:
            print(repr(e))
            raise e

    def end_keyword(self, name, attrs):
        if not self._suiteLevel:
            return
        try:
            self._wrapped.end_keyword(to_obj(attrs))
        except Exception as e:
            print(repr(e))
            raise e

    def log_message(self, msg, level="INFO"):
        if not self._suiteLevel:
            return
        try:
            self._wrapped.log_message(robot.model.Message(msg, level))
        except Exception as e:
            print(repr(e))
            raise e

    def close(self):
        self._wrapped.close()
