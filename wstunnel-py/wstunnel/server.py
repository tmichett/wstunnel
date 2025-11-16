import asyncio
import websockets
import logging
from urllib.parse import urlparse
from .restrictions import Restrictions

class UDPServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, websocket):
        self.websocket = websocket
        self.transport = None
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport
        asyncio.create_task(self.forward_from_websocket())

    def datagram_received(self, data, addr):
        asyncio.create_task(self.websocket.send(data))

    async def forward_from_websocket(self):
        while True:
            try:
                data = await self.websocket.recv()
                self.transport.sendto(data)
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception as e:
                logging.error(f"Error reading from websocket: {e}")
                break

    def error_received(self, exc):
        logging.error(f"Error received: {exc}")

    def connection_lost(self, exc):
        logging.info("UDP server connection closed")


async def handle_udp_connection(remote_host, remote_port, websocket):
    loop = asyncio.get_running_loop()
    await loop.create_datagram_endpoint(
        lambda: UDPServerProtocol(websocket),
        remote_addr=(remote_host, remote_port)
    )
    await asyncio.Future()

async def handle_tcp_connection(remote_host, remote_port, websocket):
    try:
        reader, writer = await asyncio.open_connection(remote_host, remote_port)
    except Exception as e:
        logging.error(f"Failed to connect to {remote_host}:{remote_port}: {e}")
        await websocket.close()
        return

    async def forward_to_remote():
        while True:
            try:
                data = await websocket.recv()
                writer.write(data)
                await writer.drain()
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception as e:
                logging.error(f"Error reading from websocket: {e}")
                break
        writer.close()

    async def forward_to_websocket():
        while True:
            try:
                data = await reader.read(1024)
                if not data:
                    break
                await websocket.send(data)
            except Exception as e:
                logging.error(f"Error reading from remote: {e}")
                break
        await websocket.close()

    await asyncio.gather(
        forward_to_remote(),
        forward_to_websocket()
    )


class WsServer:
    def __init__(self, config, restrictions=None):
        self.config = config
        self.host, self.port = self.parse_remote_addr(config.remote_addr)
        self.restrictions = restrictions

    def parse_remote_addr(self, remote_addr):
        parsed_uri = urlparse(remote_addr)
        return parsed_uri.hostname, parsed_uri.port

    async def handle_connection(self, websocket, path):
        logging.info(f"Client connected from {websocket.remote_address}")
        try:
            message = await websocket.recv()
            parts = message.split(":")
            if len(parts) == 3:
                protocol, remote_host, remote_port = parts
                remote_port = int(remote_port)

                if self.restrictions and not self.restrictions.is_allowed(remote_host, remote_port, path, None):
                    logging.warning(f"Connection to {remote_host}:{remote_port} is not allowed.")
                    await websocket.close()
                    return
                
                if protocol == "tcp":
                    await handle_tcp_connection(remote_host, remote_port, websocket)
                elif protocol == "udp":
                    await handle_udp_connection(remote_host, remote_port, websocket)
                else:
                    logging.error(f"Invalid protocol: {protocol}")
                    await websocket.close()
            else:
                logging.error(f"Invalid message format: {message}")
                await websocket.close()
        except websockets.exceptions.ConnectionClosed as e:
            logging.info(f"Client disconnected: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")

async def run_server(args):
    restrictions = None
    if args.restrict_config:
        restrictions = Restrictions(args.restrict_config)

    server = WsServer(args, restrictions)
    async with websockets.serve(server.handle_connection, server.host, server.port):
        logging.info(f"Server started on {server.host}:{server.port}")
        await asyncio.Future()  # run forever
