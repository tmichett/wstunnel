from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Client:
    remote_addr: str
    local_to_remote: List[str] = field(default_factory=list)
    remote_to_local: List[str] = field(default_factory=list)
    http_proxy: Optional[str] = None
    http_proxy_login: Optional[str] = None
    http_proxy_password: Optional[str] = None
    http_upgrade_path_prefix: str = "v1"
    http_headers: dict = field(default_factory=dict)
    log_lvl: str = "INFO"

@dataclass
class Server:
    remote_addr: str
    restrict_to: List[str] = field(default_factory=list)
    log_lvl: str = "INFO"
