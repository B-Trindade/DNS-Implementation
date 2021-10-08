"""TODO"""

import time
import socket
import select as s
import pickle
import dnslib as dns

class DNSresolver():
    """
    The resolver must be able to take in multiple request simultaneously,
    from the clients and from the hosts. It is responsible for navigating the
    DNS server tree through iterative lookups as well as caching recent results.
    """

    def __init__(self, question: str, cliSocket: socket.socket) -> None:
        self.question = question
        self.socket = cliSocket

        self.logs = []
        self.curr_name = question + '.'
        self.curr_addr = 53000
        pass

    def getServerIP(self):
        # sends the first message that goes to the root server
        q = dns.DNSRecord.question(self.question)
        self.socket.sendto(pickle.dumps(q), ('localhost', self.curr_addr))

        try:
            while True:
                r, w, x = s.select([self.socket], [], [])

                for ready in r:
                    if ready == self.socket:
                        response, server_addr = self.socket.recvfrom(4096)
                        response = pickle.loads(response)

                        self.logs.append(response)
                        print(response)
                        print('\n')

                        self.curr_name = self.updateName(self.curr_name) 
                        self.curr_addr = response.short()

                        if self.resolveCurrentName(self.curr_name, self.curr_addr):
                            return self.curr_addr
        finally:
            self.socket.close()

        pass

    def resolveCurrentName(self, curr_name: str, curr_addr) -> bool:
        """returns true if destination has been reached (name has been resolved)"""
        #curr_name = self.updateName(curr_name)
        if curr_name == '':
            return True
        
        q = dns.DNSRecord.question(curr_name)
        curr_addr = self.formatAddress(curr_addr)

        self.socket.sendto(pickle.dumps(q), ('localhost', curr_addr))
        return False

    def updateName(self, curr_name: str) -> str:
        print(curr_name)
        names = curr_name.split('.')
        print(names)
        new_name = ''
        if len(names) > 2:
            for i in range(len(names) - 2):
                new_name += names[i] + '.'
        elif len(names) == 2:
            new_name = names[0] + '.'
            if new_name == curr_name:
                return ''
        print(new_name)
        return new_name
    
    def formatAddress(self, curr_addr: str) -> int:
        # separates the encoded port (53.x.x.x) into different strings
        parts = curr_addr.split('.')
        # joins the segmented parts to form a port 53xxx
        port = ''
        for i in parts:
            port += i
        
        return int(port)