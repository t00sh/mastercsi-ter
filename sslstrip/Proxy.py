import logging
import socket

class Proxy:
    """
    This class implements the HTTP(s) proxy.
    It handles HTTP connections from clients and redirects to HTTPS servers.
    """

    def __init__(self, port, addr='127.0.0.1'):
        self.__port = port
        self.__addr = addr
        self.__sock = None

    def __listen(self):
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.__addr, self.__port))
        sock.listen(5)
        self.__sock = sock

    def __handle_client(self, csock, fromaddr):
        while True:
            data = csock.recv(1024)
            if data == b'':
                break
            csock.send(data)

    def __accept(self):
        while True:
            csock, fromaddr = self.__sock.accept()
            caddr, cport = fromaddr
            logging.info("New client connected ({}:{})".format(caddr, cport))

            self.__handle_client(csock, fromaddr)
            csock.close()

    def run(self):
        self.__listen()

        logging.info("Proxy listenning on {}:{}".format(
            self.__addr, self.__port))

        self.__accept()
