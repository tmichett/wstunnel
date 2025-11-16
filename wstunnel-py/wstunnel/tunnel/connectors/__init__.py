from abc import ABC, abstractmethod
import asyncio

class TunnelConnector(ABC):
    @abstractmethod
    async def connect(self, remote_addr=None):
        pass

    async def connect_with_http_proxy(self, proxy, remote_addr=None):
        raise NotImplementedError("HTTP Proxy is not supported with this connector")
