"""
Implementation of DNS server
"""

import random as rand
import socket
import threading
import sys
import time
import select as s
import dnslib as dns

def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

class DNSserver():
    """
    A server must register either a Host process or a Server process:
        - a HOST will provide a pair (hostname, PID)
        - a SERVER will provide a pair (dns, PID)
    The lookup after no ENTRY is found is implemented by the RESOLVER.
    """

    # Class Variables
    ENCODING = 'utf-8'
    CONN_HOST = 'HOST' #TODO Define this
    CONN_SERVER = '' #TODO

    def __init__(self, domain:str=None, parent:str=None) -> None:
        self.host = 'localhost' # restringe para processos internos por eficiencia
        self.port = rand.randint(53000, 53999)

        if domain is None:
            domain = "."
        self.domain = domain

        if parent is None:
            parent = ""
        self.parent = parent

        # starts the server socket using UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # select entry points
        self.entry_points = [self.socket, sys.stdin]
        pass

    def __enter__(self):
        return self

    def start(self):
        print('===================================================')
        print(f'Server hospedado em: "{self.host}:{self.port}".')
        print('===================================================\n')

        self.socket.setblocking(False)

        while True:
            r, w, x = s.select(self.entry_points, [], [])

            for ready in r:
                if ready == self.socket:
                    conn_addr, conn_type = self.receiveMessage()
                    
                    if conn_type == self.CONN_HOST or self.CONN_SERVER:
                        # spawns a thread to handle any new nodes (Host or Server)
                        reg = self.registerHandler(conn_type)
                        reg.join()
                    else:
                        #TODO: treat client with response
                        pass
                elif ready == sys.stdin:
                    cmd = input()
                    print('server> ' + cmd)
                    if cmd == 'end':
                        self.socket.close()
                    #TODO: HANDLE COMMANDS
        pass
    
    def receiveMessage(self):
        # get incoming conn's node type and return
        data, conn_addr = self.socket.recvfrom(1024)

        #TODO: IMPLEMENT SINGLE MESSAGE WHERE FIRST N BYTES SIGNAL CONNECTION TYPE
        # THIS AVOIDS HAVING TO SEND 2 DIFFERENT DNS MESSAGES str(data[:N],encoding)
        conn_type = str(data, encoding=self.ENCODING)

        return conn_addr, conn_type

    @threaded
    def registerHandler(self, conn_type):
        #TODO
        print(f'{conn_type} registrado')
        
        pass

    def generateResponse():
        pass

    def __exit__(self) -> None:
        self.socket.close()
        pass

    def __del__(self) -> None:
        self.socket.close()
        pass

def main():

    with DNSserver() as server:
        server.start()

if __name__ == '__main__':
    main()