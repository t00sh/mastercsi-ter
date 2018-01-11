#!/usr/bin/python
# -*- coding: utf-8

"""
This script implements the SSLstrip attack presented by Moxie at the BlackHat
conference, in 2008.
"""

__author__  = 'Amélie Risi, Brendan Guevel and Simon Duret'
__version__ = '0.1'
__license__ = 'GPL'
__status__  = 'Development'


from sslmitm.Options import Options
from sslmitm.ProxyHTTP import ProxyHTTP

if __name__ == "__main__":
    options = Options(__author__, __version__, __license__)
    options.parse()

    proxy = ProxyHTTP(options.port, options.verbose)
    proxy.run()
