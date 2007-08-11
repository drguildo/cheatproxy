#!/usr/bin/env python

import string
from urlparse import urlparse

from twisted.web import proxy, http
from twisted.internet import reactor

from cheatbt import CheatBT

PORT = 3456

class CheatProxy(proxy.Proxy):
    def dataReceived(self, data):
        c = CheatBT()
        headers = data.splitlines(True)
        request = headers[0].split()
        request[1] = c.cheat_url(request[1], True)
        request[2] = request[2] + "\r\n"
        headers[0] = " ".join(request)
        headers = "".join(headers)
        proxy.Proxy.dataReceived(self, headers)

#log.startLogging(sys.stdout)

if __name__ == "__main__":
    factory = http.HTTPFactory()
    factory.protocol = CheatProxy

    reactor.listenTCP(PORT, factory)
    reactor.run()
