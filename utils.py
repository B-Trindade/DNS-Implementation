from dataclasses import dataclass
from enum import Enum

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