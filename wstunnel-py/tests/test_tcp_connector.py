import pytest
from wstunnel.tunnel.connectors.tcp import TcpTunnelConnector

@pytest.mark.asyncio
async def test_tcp_tunnel_connector():
    # This test will require a running TCP server to connect to.
    # For now, we'll just instantiate the connector and check that
    # it raises a ConnectionRefusedError when no server is running.
    
    connector = TcpTunnelConnector(host='127.0.0.1', port=9999, dns_resolver=None)
    
    with pytest.raises(ConnectionRefusedError):
        await connector.connect()
