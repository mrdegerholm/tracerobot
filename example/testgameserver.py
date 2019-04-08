#!/usr/bin/env python3
import requests
from tracerobot.decorators import suite, keyword, testcase
from tracerobot.rt_state import RtState
from tracerobot.rfw_adapter import RfwAdapter


@keyword
def testlog(msg):
    pass


class TestGameServer:
    """ Game Server Acceptance Tests """

    def __init__(self, url):
        self._url = url

    class Login:
        @keyword
        def __init__(self, url, user, passw):
            self._url = url
            self._user = user
            self._passw = passw

        @keyword
        def try_login(self):
            params = {'user': self._user, 'pass': self._passw}
            r = requests.get(self._url, params=params)

            testlog('http status=%i' % r.status_code)
            if r.status_code == requests.codes.ok:
                j = r.json()
                testlog('result=%s' % j)
                return 'status' in j and j['status'] == 'OK'

            return False

    @testcase
    def test_empty_creds(self):
        login = TestGameServer.Login(self._url + "/login", user="", passw="")
        assert not login.try_login()

    @testcase
    def test_valid_creds(self):
        login = TestGameServer.Login(self._url + "/login", "markku", "3l1t3")
        assert login.try_login()

@suite
def GameServerTestSuite():
    # this is what should be replaced by some testing framwork.
    testGameServer = TestGameServer("http://localhost:5000/game")
    testGameServer.test_empty_creds()
    testGameServer.test_valid_creds()

def main():
    RtState.init()
    GameServerTestSuite()
    RtState.close()

main()
