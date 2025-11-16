import asyncio

class UDPProtocol(asyncio.DatagramProtocol):
    def __init__(self, ws_client, remote_host, remote_port):
        self.ws_client = ws_client
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.transport = None
        self.ws_transport = None
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport
        asyncio.create_task(self.start_ws_client())

    async def start_ws_client(self):
        reader, writer = await self.ws_client.open_connection(self.remote_host, self.remote_port)
        self.ws_transport = (reader, writer)
        asyncio.create_task(self.forward_remote_to_local())

    def datagram_received(self, data, addr):
        if self.ws_transport:
            self.ws_transport[1].write(data)

    async def forward_remote_to_local(self):
        while True:
            data = await self.ws_transport[0].read(1024)
            if not data:
                break
            self.transport.sendto(data)

    def error_received(self, exc):
        print(f"Error received: {exc}")

    def connection_lost(self, exc):
        print("Connection closed")


async def create_udp_tunnel(local_host, local_port, remote_host, remote_port, ws_client):
    loop = asyncio.get_running_loop()
    await loop.create_datagram_endpoint(
        lambda: UDPProtocol(ws_client, remote_host, remote_port),
        local_addr=(local_host, local_port)
    )
    await asyncio.Future()
