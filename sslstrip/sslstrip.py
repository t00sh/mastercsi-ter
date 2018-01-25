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

FORWARD_HOST = 'www.t0x0sh.org'
FORWARD_PORT = 80
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 4242
BUFFER_SIZE = 65537

class SSLstrip:
    def __listen(self):
        """ Create the listenning socket for Proxy
        """
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((PROXY_HOST, PROXY_PORT))
        sock.listen(5)
        self.__sock = sock

    def __handle_client(self, csock, fromaddr):
        """ Handle clients connections, and forward requests.
        """
        fw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fw_sock.connect((FORWARD_HOST, FORWARD_PORT))

        csock.settimeout(2)
        fw_sock.settimeout(2)

        while True:
            data = csock.recv(BUFFER_SIZE)
            if len(data) == 0:
                fw_sock.close()
                break

            fw_sock.send(data)

            data = fw_sock.recv(BUFFER_SIZE)
            while len(data) > 0:
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
            except:
                print("Timeout...")
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
