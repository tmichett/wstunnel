from . import TunnelConnector
from .tcp import TcpTunnelConnector
from .udp import UdpTunnelConnector
from .. import LocalProtocol, LocalProtocolType

class Socks5TunnelConnector(TunnelConnector):
    def __init__(self, dns_resolver, connect_timeout=10, so_mark=None):
        self.dns_resolver = dns_resolver
        self.connect_timeout = connect_timeout
        self.so_mark = so_mark

    async def connect(self, remote_addr=None):
        if not remote_addr:
            raise ValueError("Remote address is required for SOCKS5 connector")

        if remote_addr.protocol.protocol_type == LocalProtocolType.TCP:
            connector = TcpTunnelConnector(
                host=remote_addr.host,
                port=remote_addr.port,
                dns_resolver=self.dns_resolver,
                connect_timeout=self.connect_timeout,
                so_mark=self.so_mark,
            )
            return await connector.connect()
        elif remote_addr.protocol.protocol_type == LocalProtocolType.UDP:
            connector = UdpTunnelConnector(
                host=remote_addr.host,
                port=remote_addr.port,
                dns_resolver=self.dns_resolver,
                connect_timeout=self.connect_timeout,
                so_mark=self.so_mark,
            )
            return await connector.connect()
        else:
            raise ValueError(f"Unsupported protocol for SOCKS5 connector: {remote_addr.protocol.protocol_type}")

    async def connect_with_http_proxy(self, proxy, remote_addr=None):
        if not remote_addr:
            raise ValueError("Remote address is required for SOCKS5 connector")

        if remote_addr.protocol.protocol_type == LocalProtocolType.TCP:
            connector = TcpTunnelConnector(
                host=remote_addr.host,
                port=remote_addr.port,
                dns_resolver=self.dns_resolver,
                connect_timeout=self.connect_timeout,
                so_mark=self.so_mark,
            )
            return await connector.connect_with_http_proxy(proxy)
        else:
            raise ValueError("SOCKS5 UDP cannot use http proxy to connect to destination")
