import SimpleHTTPServer
import SocketServer

class ProxyHTTP:
    """
    This class implements the HTTP proxy.
    It handles HTTP connections from clients and redirects to HTTPS servers.
    """

    def __init__(self, port, verbose):
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler

        self.__port = port
        self.__httpd = SocketServer.TCPServer(("", port), handler)
        self.__verbose = verbose

    def run(self):
        if self.__verbose:
            print("[+] Running proxy on port {}".format(self.__port))

        self.__httpd.serve_forever()
