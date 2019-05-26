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
        'set_auto_trace_kwtype'
    ]

    def __init__(self, logfile='output.xml'):
        self._settings = {'logfile': logfile}
        self._adapter = RobotAdapter(None)
        self._writer = None

    def __getattribute__(self, name):
        # Get attributes using base class to avoid infinite recursion
        def _getattr(attr):
            return super(Listener, self).__getattribute__(attr)

        try:
            adapter = _getattr('_adapter')
            return getattr(adapter, name)
        except AttributeError:
            return _getattr(name)

    def configure(self, **kwargs):
        self._settings.update(kwargs)
        assert 'logfile' in self._settings, 'Output filename required'

        self._writer = XmlLogger(self._settings['logfile'])
        self._adapter.writer = self._writer

    def close(self):
        if self._writer:
            self._writer.close()

        self._writer = None
        self._adapter = None
