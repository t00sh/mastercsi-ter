import sys
import getopt

class Options:
    """
    Handle command line arguments.
    """

    def __init__(self, author, version, copying):
        self.author = author
        self.version = version
        self.copying = copying

        self.__port = self.defaultPort
        self.__verbose = False
        self.__logFile = None

    def parse(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:],
                                       'hl:p:v',
                                       ['help', 'log=', 'port=', 'verbose'])
        except getopt.GetoptError as err:
            print(str(err))
            print("Try: {} -h".format(sys.argv[0]))
            sys.exit(1)


        for o, a in opts:
            if o in ('-h', '--help'):
                self.usage()
                sys.exit(0)
            elif o in ('-l', '--log'):
                self.__logFile = a
            elif o in ('-p', '--port'):
                self.__port = int(a)
            elif o in ('-v', '--verbose'):
                self.__verbose = True
            else:
                assert False, "unhandled option"

    def usage(self):
        print("{} v{} ({}).\n".format(sys.argv[0],
                                      self.version,
                                      self.author))

        print("Usage: {} [OPTIONS]".format(sys.argv[0]))
        print("OPTIONS")
        print("   --help, -h               Print this help message")
        print("   --log, -l       <file>   Log traffic into a file")
        print("   --port, -p      <port>   " \
              "Listening port (default: {})".format(self.defaultPort))
        print("   --verbose, -v            Increase verbosity")

    @property
    def defaultPort(self):
        return 31337

    @property
    def port(self):
        return self.__port

    @property
    def verbose(self):
        return self.__verbose

    @property
    def logFile(self):
        return self.__logFile
