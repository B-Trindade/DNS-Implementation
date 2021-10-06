"""TODO"""

import socket
import multiprocessing
import time
from functools import lru_cache

class Client():
    """TODO"""
    
    def __init__(self):
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