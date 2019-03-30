from robot.output.xmllogger import XmlLogger
from tracerobot.wrapperlistener import WrapperListener
from tracerobot.rfw_adapter import RfwAdapter

DEFAULT_STATE = None

class RtState(object):

    def __init__(self, logfile):
        self._config = {"logfile": logfile}
        self._logger = XmlLogger(logfile)
        self._listener = WrapperListener(self._logger)
        self._adapter = RfwAdapter(self._listener)

    def _close(self):
        self._listener.close()
        print("tracerobot: log file written to " + self._config["logfile"])

    @staticmethod
    def init(logfile="output.xml"):
        state = RtState(logfile)

        global DEFAULT_STATE
        DEFAULT_STATE = state

    @staticmethod
    def close():
        RtState.get()._close()

    @staticmethod
    def get():
        global DEFAULT_STATE
        state = DEFAULT_STATE
        assert state, "State is NULL"
        return state

    @staticmethod
    def get_adapter():
        return RtState.get()._adapter
