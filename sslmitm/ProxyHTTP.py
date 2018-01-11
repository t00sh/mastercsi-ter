import SimpleHTTPServer
import SocketServer
import logging

class ProxyHTTP:
    """
    This class implements the HTTP proxy.
    It handles HTTP connections from clients and redirects to HTTPS servers.
    """

    def __init__(self, port):
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler

        self.__port = port
        self.__httpd = SocketServer.TCPServer(("", port), handler)

    def run(self):
        logging.info("Running proxy on port {}".format(self.__port))
        self.__httpd.serve_forever()
