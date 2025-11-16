from .config import Client, Server
from .tunnel.client.client import create_client
from .tunnel.server.server import create_server

async def run_client(args: Client):
    """
    Runs the wstunnel client.
    """
    client = await create_client(args)
    print(f"Running client with config: {client.config}")

async def run_server(args: Server):
    """
    Runs the wstunnel server.
    """
    server = await create_server(args)
    print(f"Running server with config: {server.config}")
