from abc import ABC, abstractmethod

class TunnelListener(ABC):
    @abstractmethod
    async def listen(self):
        pass
