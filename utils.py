from dataclasses import dataclass
from enum import Enum

class TypeEnum(Enum):
    HOST = 'host'
    SERVER = 'server'

@dataclass
class RegisterMsg:
    type: TypeEnum
    name: str

@dataclass
class RegisterResultMsg:
    success: bool
    error_text: str = None