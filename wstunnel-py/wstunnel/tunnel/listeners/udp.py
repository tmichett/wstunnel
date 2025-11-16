from . import TunnelListener

class UdpTunnelListener(TunnelListener):
    def __init__(self, bind_addr, dest, timeout=None):
        self.bind_addr = bind_addr
        self.dest = dest
        self.timeout = timeout

    async def listen(self):
        # The implementation for UDP listeners will be more complex than TCP,
        # as asyncio does not provide a high-level API for UDP servers in the
        # same way it does for TCP. We will need to create a custom UDP
        # server implementation.
        raise NotImplementedError("UDP support is not yet implemented")
