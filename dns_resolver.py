"""TODO"""

import time
import grpc
import socket

class DNSresolver(root):
    """
    The resolver must be able to take in multiple request simultaneously,
    from the clients and from the hosts. It is responsible for navigating the
    DNS server tree through iterative lookups as well as caching recent results.
    """

    def __init__(self, root) -> None:
        self.cache = Cache(root)
        pass

class Cache():
    """Implements our simple cache structure"""
    
    def __init__(self, root) -> None:
        self.dns_list = [root]
        pass
