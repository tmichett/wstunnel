from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple

class LocalProtocolType(Enum):
    TCP = auto()
    UDP = auto()
    STDIO = auto()
    SOCKS5 = auto()
    TPROXY_TCP = auto()
    TPROXY_UDP = auto()
    HTTP_PROXY = auto()
    REVERSE_TCP = auto()
    REVERSE_UDP = auto()
    REVERSE_SOCKS5 = auto()
    REVERSE_HTTP_PROXY = auto()
    REVERSE_UNIX = auto()
    UNIX = auto()

@dataclass
class LocalProtocol:
    protocol_type: LocalProtocolType
    proxy_protocol: bool = False
    timeout: Optional[int] = None
    credentials: Optional[Tuple[str, str]] = None
    path: Optional[str] = None

    def is_reverse_tunnel(self) -> bool:
        return self.protocol_type in [
            LocalProtocolType.REVERSE_TCP,
            LocalProtocolType.REVERSE_UDP,
            LocalProtocolType.REVERSE_SOCKS5,
            LocalProtocolType.REVERSE_UNIX,
            LocalProtocolType.REVERSE_HTTP_PROXY,
        ]
    
    def is_dynamic_reverse_tunnel(self) -> bool:
        return self.protocol_type in [
            LocalProtocolType.REVERSE_SOCKS5,
            LocalProtocolType.REVERSE_HTTP_PROXY,
        ]

@dataclass
class RemoteAddr:
    protocol: LocalProtocol
    host: str
    port: int
