#!/usr/bin/env python

"""A basic HTTP proxy server that intercepts communication with
BitTorrent trackers and optionally spoofs the amount of data
uploaded. Free from artificial colours and preservatives. Web 2.0
compatible."""

import getopt
import logging
import select
import socket
import sys
import urlparse

import BaseHTTPServer
import SocketServer

import cheatbt

class CheatHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """Used by HTTPServer to handle HTTP requests"""

    mappings = {}

    def do_GET(self):
        """Called by BaseHTTPRequestHandler when a GET request is
        received from a client."""

        cheatpath = cheatbt.cheat(self.path, CheatHandler.mappings)

        logger = logging.getLogger("cheatproxy")
        logger.info(cheatpath)

        (scheme, netloc, path, params, query, fragment) = \
            urlparse.urlparse(cheatpath, 'http')

        # TODO: https support.
        if scheme != 'http' or fragment or not netloc:
            self.send_error(501)
            return

        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            if self._connect_to(netloc, soc):
                request = urlparse.urlunparse(('', '', path, params, query, ''))
                soc.send("%s %s %s\r\n" % (self.command, request,
                                           self.request_version))
                self.headers['Connection'] = 'close'
                del self.headers['Proxy-Connection']
                # This is naughty. But rfc822.Message, which self.headers is a
                # subclass of, insists on converting headers to lowercase when
                # accessed conventionally (i.e. as a dict).
                for header in self.headers.headers:
                    header = header.strip() + '\r\n'
                    soc.send(header)
                    logger.debug(repr(header))
                soc.send("\r\n")
                self._read_write(soc)
        finally:
            soc.close()
            self.connection.close()

    def _connect_to(self, netloc, soc):
        """Attempt to establish a connection to the tracker."""

        i = netloc.find(':')
        if i >= 0:
            host_port = (netloc[:i], int(netloc[i+1:]))
        else:
            host_port = (netloc, 80)

        try:
            soc.connect(host_port)
        except socket.error:
            return False

        return True

    def _read_write(self, soc, max_idling=20):
        """Pass data between the remote server and the client. I
        think."""

        logger = logging.getLogger("cheatproxy")

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
                    try:
                        data = i.recv(8192)
                        if data:
                            out.send(data)
                            count = 0
                    except socket.error, msg:
                        logger.info(msg)
            else:
                pass
            if count == max_idling:
                break

class CheatProxy(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    def __init__(self, host, port):
        BaseHTTPServer.HTTPServer.__init__(self, (host, port),
                CheatHandler)

def usage():
    """Prints usage information and exits."""

    print """
usage: %s [-b host] [-p port] [-f file] [-v] [-d] [-h]

  -b host  IP or hostname to bind to. Default is localhost.
  -p port  Port to listen on. Default is 8000.
  -f file  Mappings file.
  -v       Verbose output.
  -d       Debug output.
  -h       What you're reading.
""" % sys.argv[0]
    sys.exit(1)

def main():
    host = "localhost"
    port = 8000

    rootlogger = logging.getLogger("")
    ch = logging.StreamHandler()
    ch.setFormatter(
        logging.Formatter("%(asctime)s:%(name)s:%(levelname)s %(message)s"))
    rootlogger.addHandler(ch)

    try:
        opts, _ = getopt.getopt(sys.argv[1:], "b:f:p:hvd")
    except getopt.GetoptError:
        usage()

    for opt, val in opts:
        if opt == "-b":
            host = val
        if opt == "-p":
            port = int(val)
        if opt == "-f":
            CheatHandler.mappings = cheatbt.load_mappings(val)
        if opt == "-v":
            rootlogger.setLevel(logging.INFO)
        if opt == "-d":
            rootlogger.setLevel(logging.DEBUG)
        if opt == "-h":
            usage()

    httpd = CheatProxy(host, port)

    logger = logging.getLogger("cheatproxy")
    logger.info("listening on %s:%d" % (host, port))

    httpd.serve_forever()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.shutdown()
        sys.exit()
