"""
Implementation of DNS server
"""

import random as rand
import socket
import threading
import sys
import select as s

class DNSserver():
    """
    A server must register either a Host process or a Server process:
        - a HOST will provide a pair (hostname, PID)
        - a SERVER will provide a pair (dns, PID)
    The lookup after no ENTRY is found is implemented by the RESOLVER.
    """

    # Class Variables
    ENCODING = 'utf-8'
    CONN_HOST = '' #TODO Define this
    CONN_SERVER = '' #TODO

    def __init__(self, domain:str=None, parent:str=None) -> None:
        self.host = 'localhost'
        self.port = rand.randint(53000, 53999)

        if domain is None:
            domain = "."
        self.domain = domain

        if parent is None:
            parent = ""
        self.parent = parent

        # starts the server socket using UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # select entry points
        self.entry_points = [sys.stdin]
        pass

    def start(self):
        print('===================================================')
        print(f'Server hospedado em: "{self.host}:{self.port}".\n')
        print('===================================================')

        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.socket.setblocking(False)

        while True:
            r, w, x = s.select(self.entry_points, [], [])

            for ready in r:
                if ready == self.socket:
                    conn_sckt, conn_addr, conn_type = acceptConnection()
                    
                    if conn_type == CONN_HOST or CONN_SERVER:
                        # spawns a thread to handle any new nodes (Host or Server)
                        reg = threading.Thread(target=registerHandler, args=())
                        reg.start()
                    else:
                        #TODO: treat client with response
                        pass
                elif ready == sys.stdin:
                    cmd = input()
                    #TODO: HANDLE COMMANDS
        pass
    
    def acceptConnection(self):
        conn_sckt, conn_addr = self.socket.accept()

        # get incoming conn's node type and return
        data = conn_sckt.recv(1024)
        #TODO: IMPLEMENT SINGLE MESSAGE WHERE FIRST N BYTES SIGNAL CONNECTION TYPE
        # THIS AVOIDS HAVING TO SEND 2 DIFFERENT DNS MESSAGES str(data[:N],encoding)
        conn_type = str(data, encoding=ENCODING)

        return conn_sckt, conn_addr, conn_type

    def registerHandler(self):
        #TODO


        pass
