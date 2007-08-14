#!/usr/bin/env python

"""A basic HTTP proxy server that intercepts communication with
BitTorrent trackers and optionally spoofs the amount of data
uploaded. Free from artificial colours and preservatives. Web 2.0
compatible."""

import getopt
import select
import socket
import sys
import urlparse

import BaseHTTPServer
import SocketServer

from cheatbt import CheatBT

TRACKERS_FILE = "trackers"

class CheatHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """Used by CheatServer/HTTPServer to handle HTTP requests"""

    def do_GET(self):
        """Called by BaseHTTPRequestHandler when a GET request is
        received from a client."""

        cheat = CheatBT(TRACKERS_FILE)
        cheatpath = cheat.cheat_url(self.path)

        (scheme, netloc, path, params, query, fragment) = \
            urlparse.urlparse(cheatpath, 'http')

        # TODO: https support.
        if scheme != 'http' or fragment or not netloc:
            self.send_error(501, "bad url %s" % cheatpath)
            return

        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            if self._connect_to(netloc, soc):
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
        """Attempt to connect to establish a connection to the remote
        server."""

        i = netloc.find(':')
        if i >= 0:
            host_port = (netloc[:i], int(netloc[i+1:]))
        else:
            host_port = (netloc, 80)

        try:
            soc.connect(host_port)
        except socket.error, msg:
            self.send_error(502, msg)
            return False

        return True

    def _read_write(self, soc, max_idling=20):
        """Pass data between the remote server and the client. I
        think."""

        rlist = [self.connection, soc]
        wlist = []
        count = 0
        while True:
            count += 1
            (ins, _, exs) = select.select(rlist, wlist, rlist, 3)
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

class CheatServer(SocketServer.ThreadingMixIn,
                  BaseHTTPServer.HTTPServer):
    """HTTPServer with added thready goodness. I think."""
    pass

def usage():
    """Prints usage information and exits."""

    print """
usage: %s [-b host] [-p port] [-f file] [-v] [-h]

  -b host  IP or hostname to bind to. Default is localhost.
  -p port  Port to listen on. Default is 8000.
  -f file  Mappings file.
  -v       Verbose output.
  -h       What you're reading.
""" % sys.argv[0]
    sys.exit(1)

def main():
    host = "localhost"
    port = 8000

    try:
        opts, _ = getopt.getopt(sys.argv[1:], "b:f:p:hv")
    except getopt.GetoptError:
        usage()

    for opt, val in opts:
        if opt == "-b":
            host = val
        if opt == "-p":
            port = int(val)
        if opt == "-f":
            global TRACKERS_FILE
            TRACKERS_FILE = val
        if opt == "-v":
            pass
        if opt == "-h":
            usage()

    httpd = CheatServer((host, port), CheatHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
