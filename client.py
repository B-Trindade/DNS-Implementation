"""TODO"""

import time
import socket
import random as rand
import multiprocessing
from functools import lru_cache
from dns_resolver import DNSresolver as Resolver

class Client():
    """TODO"""
    
    def __init__(self):
        self.host = 'localhost'
        self.port = rand.randint(50000, 52999)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.resolver = Resolver()
        pass


def main():
    cliSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('client started')
    try:
        host = input('Host: ')
        port = input('Port: ')
        cliSock.sendto("HOST".encode('utf-8'), (host, int(port)))  
        print('fui registrado?')
        cliSock.sendto("www.google.com".encode('utf-8'), (host, int(port)))
    finally:
        cliSock.close()

if __name__ == '__main__':
    main()