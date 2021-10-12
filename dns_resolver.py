"""TODO"""

import time
import socket
import select as s
import pickle
import dnslib as dns
from functools import lru_cache

from utils import SubdomainNotFoundMsg

TIMEOUT = 3

class DNSresolver():
    """
    The resolver must be able to take in multiple request simultaneously,
    from the clients and from the hosts. It is responsible for navigating the
    DNS server tree through iterative lookups as well as caching recent results.
    """

    def __init__(self, question: str, cliSocket: socket.socket) -> None:
        self.question = question
        self.socket = cliSocket
        self.socket.settimeout(TIMEOUT)

        self.logs = []
        self.curr_name = question + '.'
        self.curr_addr = 53000
        pass
    
    #@lru_cache
    def getServerIP(self):
        # sends the first message that goes to the root server
        q = dns.DNSRecord.question(self.question)
        self.socket.sendto(pickle.dumps(q), ('localhost', self.curr_addr))

        try:
            while True:
                response, server_addr = self.socket.recvfrom(4096)
                response = pickle.loads(response)

                if type(response) == dns.DNSRecord:
                    self.logs.append(response)
                    self.updateName()
                    self.curr_addr = response.short()

                    if self.resolveCurrentName(self.curr_name, self.curr_addr):
                        return self.curr_addr.replace('.', '')

                elif type(response) == SubdomainNotFoundMsg:
                    return f'O subdomínio {response.subdomain} no servidor {server_addr} não foi encontrado.'

                else:
                    return f'O servidor {server_addr} retornou uma mensagem inesperada.'

        except socket.timeout:
            return ('Não foi possível encontrar o endereço informado.'
            'Durante a busca iterativa, um dos servidores não respondeu '
            'dentro do tempo esperado.')

    def resolveCurrentName(self, curr_name: str, curr_addr) -> bool:
        """returns true if destination has been reached (name has been resolved)"""
        #curr_name = self.updateName(curr_name)
        if curr_name == '':
            return True
        
        q = dns.DNSRecord.question(curr_name)
        curr_addr = self.formatAddress(curr_addr)

        self.socket.sendto(pickle.dumps(q), ('localhost', curr_addr))
        return False

    def updateName(self):
        names = self.curr_name.split('.')
        new_name = ''
        if len(names) > 2:
            for i in range(len(names) - 2):
                new_name += names[i] + '.'
        elif len(names) == 2:
            new_name = names[0] + '.'
            if new_name == self.curr_name:
                self.curr_name = ''
                return
        self.curr_name = new_name
    
    def formatAddress(self, curr_addr: str) -> int:
        # separates the encoded port (53.x.x.x) into different strings
        parts = curr_addr.split('.')
        # joins the segmented parts to form a port 53xxx
        port = ''
        for i in parts:
            port += i
        
        return int(port)