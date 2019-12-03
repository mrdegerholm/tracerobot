from robot.output.xmllogger import XmlLogger
from tracerobot.adapter import RobotAdapter


class Listener:
    ACTIONS = [
        'configure',
        'close',
        'start_suite',
        'start_test',
        'start_keyword',
        'end_suite',
        'end_test',
        'end_keyword',
        'log_message',
        'start_auto_trace',
        'stop_auto_trace',
        'set_auto_trace_kwtype',
        'get_writer'
    ]

    def __init__(self):
        self._adapter = None
        self._writer = None
        self._settings = {
            "robot_output": "output.xml",
            "autotrace_privates": False,
            "autotrace_libpaths": []
        }

    def __getattribute__(self, name):
        # Get attributes using base class to avoid infinite recursion
        def _getattr(attr):
            return super(Listener, self).__getattribute__(attr)

        try:
            adapter = _getattr('_adapter')
            return getattr(adapter, name)
        except AttributeError:
            return _getattr(name)

    def configure(self, settings=None):
        if settings:
            self._settings.update(settings)

        autotracer_config = {
            "trace_privates": self._settings["autotrace_privates"],
            "trace_libpaths": self._settings["autotrace_libpaths"]
        }

        self._writer = XmlLogger(self._settings['robot_output'])
        self._adapter = RobotAdapter(self._writer, autotracer_config)

    def close(self):
        if self._writer:
            self._writer.close()

        self._writer = None
        self._adapter = None

    def register_to_module_namespace(self, ns_dict):
        # Allow using listener methods from module root,
        # e.g. tracerobot.start_suite()
        for name in self.ACTIONS:
            ns_dict[name] = getattr(self, name)
