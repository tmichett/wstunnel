import websockets
import logging
import asyncio
import os

class WsClient:
    def __init__(self, config):
        self.config = config

    async def connect_to_server(self, remote_addr, local_reader, local_writer):
        uri = self.config.remote_addr
        try:
            async with websockets.connect(uri) as websocket:
                logging.info(f"Connected to {uri}")
                await websocket.send(f"tcp:{remote_addr[0]}:{remote_addr[1]}")

                async def forward_local_to_remote():
                    while True:
                        try:
                            data = await local_reader.read(1024)
                            if not data:
                                break
                            await websocket.send(data)
                        except asyncio.CancelledError:
                            break
                        except Exception as e:
                            logging.error(f"Error reading from local: {e}")
                            break
                    await websocket.close()

                async def forward_remote_to_local():
                    while True:
                        try:
                            data = await websocket.recv()
                            local_writer.write(data)
                            await local_writer.drain()
                        except websockets.exceptions.ConnectionClosed:
                            break
                        except asyncio.CancelledError:
                            break
                        except Exception as e:
                            logging.error(f"Error reading from websocket: {e}")
                            break
                    local_writer.close()

                await asyncio.gather(
                    forward_local_to_remote(),
                    forward_remote_to_local()
                )
        except Exception as e:
            logging.error(f"Failed to connect to {uri}: {e}")

    async def open_connection(self, remote_host, remote_port, protocol):
        r, w = os.pipe()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_running_loop().connect_read_pipe(lambda: protocol, os.fdopen(r))

        writer = await asyncio.get_running_loop().connect_write_pipe(asyncio.streams.FlowControlMixin, os.fdopen(w))


        async def forward_to_ws(websocket):
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                await websocket.send(data)
            await websocket.close()

        async def forward_from_ws(websocket):
            while True:
                try:
                    data = await websocket.recv()
                    writer.write(data)
                    await writer.drain()
                except websockets.exceptions.ConnectionClosed:
                    break
            writer.close()

        async def coro():
            uri = self.config.remote_addr
            async with websockets.connect(uri) as websocket:
                await websocket.send(f"{protocol}:{remote_host}:{remote_port}")
                await asyncio.gather(
                    forward_to_ws(websocket),
                    forward_from_ws(websocket)
                )

        asyncio.create_task(coro())
        return reader, writer
