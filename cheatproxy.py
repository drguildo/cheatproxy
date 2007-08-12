#!/usr/bin/env python

import getopt
import select
import socket
import string
import urlparse

import BaseHTTPServer
import SocketServer

from cheatbt import CheatBT

class CheatHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        c = CheatBT()
        print "Before: " + self.path
        cheatpath = c.cheat_url(self.path, True)
        print "After: " + cheatpath

        (scheme, netloc, path, params, query, fragment) = \
            urlparse.urlparse(cheatpath, 'http')

        if scheme != 'http' or fragment or not netloc:
            self.send_error(400, "bad url %s" % cheatpath)
            return

        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            if self._connect_to(netloc, soc):
                self.log_request()
                request = urlparse.urlunparse(('', '', path, params, query, ''))
                soc.send("%s %s %s\r\n" % (self.command, request,
                                           self.request_version))
                self.headers['Connection'] = 'close'
                del self.headers['Proxy-Connection']
                for key_val in self.headers.items():
                    soc.send("%s: %s\r\n" % key_val)
                soc.send("\r\n")
                self._read_write(soc)
        finally:
            soc.close()
            self.connection.close()

    def _connect_to(self, netloc, soc):
        i = netloc.find(':')
        if i >= 0:
            host_port = (netloc[:i], int(netloc[i+1:]))
        else:
            host_port = (netloc, 80)

        try:
            soc.connect(host_port)
        except socket.error, arg:
            try:
                msg = arg[1]
            except:
                msg = arg
            self.send_error(404, msg)
            return False

        return True

    def _read_write(self, soc, max_idling=20):
        iw = [self.connection, soc]
        ow = []
        count = 0
        while True:
            count += 1
            (ins, _, exs) = select.select(iw, ow, iw, 3)
            if exs:
                break
            if ins:
                for i in ins:
                    if i is soc:
                        out = self.connection
                    else:
                        out = soc
                    data = i.recv(8192)
                    if data:
                        out.send(data)
                        count = 0
            else:
                pass
            if count == max_idling:
                break

        """
        c = CheatBT()
        headers = data.splitlines(True)
        request = headers[0].split()
        request[1] = c.cheat_url(request[1], True)
        request[2] = request[2] + "\r\n"
        headers[0] = " ".join(request)
        headers = "".join(headers)
        """

class CheatServer(SocketServer.ThreadingMixIn,
                  BaseHTTPServer.HTTPServer):
    pass

if __name__ == "__main__":
    httpd = CheatServer(('localhost', 31337), CheatHandler)
    httpd.serve_forever()
