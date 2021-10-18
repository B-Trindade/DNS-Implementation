from dataclasses import dataclass
from enum import Enum

TIMEOUT = 3
CMD_END = 'end'

class TypeEnum(Enum):
    HOST = 'Host'
    SERVER = 'Server'

@dataclass
class RegisterMsg:
    type: TypeEnum
    name: str

@dataclass
class RegisterResultMsg:
    success: bool
    full_domain: str = None
    error_text: str = None

@dataclass
class PingMsg:
    name: str

@dataclass
class PingResultMsg:
    value: bool

@dataclass
class SubdomainNotFoundMsg:
    subdomain: str