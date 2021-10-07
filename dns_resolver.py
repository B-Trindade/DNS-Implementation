"""TODO"""

import time
import socket
import select as s
import dnslib as dns

class DNSresolver():
    """
    The resolver must be able to take in multiple request simultaneously,
    from the clients and from the hosts. It is responsible for navigating the
    DNS server tree through iterative lookups as well as caching recent results.
    """

    def __init__(self, question, cliSocket) -> None:
        self.question = question
        self.socket = cliSocket

        self.logs = []
        pass

    def getServerIP(self):
        try:
            while True:
                r, w, x = s.select([self.socket], [], [])

                for ready in r:
                    if ready == self.socket:
                        response, client_addr = self.socket.recvfrom(4096)
                        response = dns.DNSRecord.parse(response)

                        self.logs.append(response)

                        curr_name = response.questions[0]
                        curr_addr = int(response.short())

                        resolveCurrentName(curr_name, curr_addr)

        finally:
            self.socket.close()

        pass

    def resolveCurrentName(self, curr_name: str, curr_addr) -> str:
        
        
        pass
