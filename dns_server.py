"""
Implementation of DNS server
"""

class DNSserver():
    """
    A server must register either a Host process or a Server process:
        - a HOST will provide a pair (hostname, PID)
        - a SERVER will provide a pair (dns, PID)
    The lookup after no ENTRY is found is implemented by the RESOLVER.
    """

    def __init__(self, domain: str, parent) -> None:
        pass