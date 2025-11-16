import websockets
from websockets.datastructures import Headers
from .handshake import manual_handshake
from websockets import WebSocketClientProtocol

async def connect(request_id: str, client, dest_addr):
    """
    Connects to the websocket server and performs the handshake.
    """
    uri = f"{client.config.remote_addr.rstrip('/')}/{client.config.http_upgrade_path_prefix}/events"
    
    headers = client.config.http_headers

    try:
        reader, writer = await manual_handshake(uri, headers)
        
        # After a successful handshake, we can wrap the connection
        # in a WebSocketClientProtocol object to handle the websocket protocol.
        # This part of the implementation is still pending.
        
        print(f"Successfully connected to {uri} via manual handshake")
        
        # For now, just close the connection
        writer.close()
        await writer.wait_closed()

    except Exception as e:
        print(f"Failed to connect to {uri}: {e}")
