from dataclasses import dataclass
from wstunnel.config import Server as ServerConfig

@dataclass
class WsServer:
    config: ServerConfig

    async def serve(self, restrictions):
        # Implementation to start the server and handle connections
        pass

async def create_server(config: ServerConfig) -> WsServer:
    # Factory function to create a WsServer instance
    return WsServer(config=config)
