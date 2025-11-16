import asyncio
import uuid
from dataclasses import dataclass
from wstunnel.config import Client as ClientConfig
from .. import RemoteAddr
from ..transport import websocket as ws_transport

@dataclass
class WsClient:
    config: ClientConfig

    async def connect_to_server(self, request_id: str, remote_cfg: RemoteAddr, duplex_stream):
        return await ws_transport.connect(request_id, self, remote_cfg)

    async def run_tunnel(self, tunnel_listener):
        # Implementation for running a standard tunnel
        pass

    async def run_reverse_tunnel(self, remote_addr: RemoteAddr, connector):
        # Implementation for running a reverse tunnel
        pass

async def create_client(config: ClientConfig) -> WsClient:
    # Factory function to create a WsClient instance
    client = WsClient(config=config)
    
    # In a real implementation, we would likely have more setup here,
    # like initializing a connection pool.
    
    # For now, let's just test a single connection.
    # We will need a RemoteAddr object to test the connection.
    # This is a placeholder.
    remote_addr = RemoteAddr(protocol=None, host="localhost", port=8080)
    await client.connect_to_server(str(uuid.uuid4()), remote_addr, None)
    
    return client
