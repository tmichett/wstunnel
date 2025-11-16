import asyncio
from . import TunnelListener

class TcpTunnelListener(TunnelListener):
    def __init__(self, bind_addr, dest, proxy_protocol=False):
        self.bind_addr = bind_addr
        self.dest = dest
        self.proxy_protocol = proxy_protocol

    async def listen(self):
        server = await asyncio.start_server(
            self.handle_connection, self.bind_addr[0], self.bind_addr[1]
        )

        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f'Serving on {addrs}')

        async with server:
            await server.serve_forever()

    async def handle_connection(self, reader, writer):
        # The implementation for handling a new TCP connection will go here.
        # This will involve creating a RemoteAddr object and yielding the
        # reader/writer streams to the tunnel.
        print("New TCP connection")
        writer.close()
        await writer.wait_closed()
