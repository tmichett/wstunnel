import asyncio
from .ws_client import WsClient

async def handle_tcp_tunnel(reader, writer, ws_client, remote_host, remote_port):
    ws_reader, ws_writer = await ws_client.open_connection(remote_host, remote_port)

    async def forward_local_to_remote():
        while True:
            data = await reader.read(1024)
            if not data:
                break
            ws_writer.write(data)
            await ws_writer.drain()
        ws_writer.close()

    async def forward_remote_to_local():
        while True:
            data = await ws_reader.read(1024)
            if not data:
                break
            writer.write(data)
            await writer.drain()
        writer.close()

    await asyncio.gather(
        forward_local_to_remote(),
        forward_remote_to_local()
    )

async def create_tcp_tunnel(local_host, local_port, remote_host, remote_port, ws_client):
    server = await asyncio.start_server(
        lambda r, w: handle_tcp_tunnel(r, w, ws_client, remote_host, remote_port),
        local_host,
        local_port
    )
    async with server:
        await server.serve_forever()
