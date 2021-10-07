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
import pickle
from utils import *

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
    CONN_SERVER = 'SERVER' #TODO
    DOMAINS = [] # domain availability

    def __init__(self) -> None:
        self.host = 'localhost' # restringe para processos internos por eficiencia
        self.port = rand.randint(53000, 53999)
        
        self.domain = input('Entre com o nome do domínio (para root use "."): ')
        self.parent_ip = input('Entre com o endereço IPv4 do server pai: ')
        self.parent_port = input('Entre com a porta do server pai: ')

        self.hosts = {}
        self.servers = {}

        # starts the server socket using UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        # select entry points
        self.entry_points = [self.socket, sys.stdin]

        self.lock = threading.Lock()
        pass

    def __enter__(self):
        return self

    def start(self):
        print('\n===================================================')
        print(f'Server hospedado em: "{self.host}:{self.port}".')
        print('===================================================\n')

        #self.socket.setblocking(False)
        try:
            while True:
                r, w, x = s.select(self.entry_points, [], [])

                for ready in r:
                    if ready == self.socket:
                        msg, addr = self.receiveMessage()

                        if msg is RegisterMsg:
                            self.registerHandler(msg, addr)
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
        except:
            print('Servidor encerrado.')
        pass
    
    def receiveMessage(self):
        # get incoming conn's node type and return
        data, addr = self.socket.recvfrom(1024)

        data = pickle.loads(data)

        return data, addr

    @threaded
    def registerHandler(self, msg: RegisterMsg, addr):
        
        while True:

            lock.acquire()
            if msg.type == TypeEnum.HOST:
                self.hosts[msg.name] = addr
                break
            elif msg.type == TypeEnum.SERVER:
                self.servers[msg.name] = addr
                break

        print(f'-> Novo {msg.type} registrado:')
        print(f'    -{msg.name}     -{addr}')
        
        pass

    def generateResponse():
        pass

    def __exit__(self, exception_type, exception_value, traceback) -> None:
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