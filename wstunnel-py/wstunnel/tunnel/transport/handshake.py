import asyncio
from urllib.parse import urlparse
import base64
import os
from websockets.http import read_response
from websockets.exceptions import InvalidUpgrade

async def manual_handshake(uri, headers):
    """
    Performs a manual websocket handshake.
    """
    parsed_uri = urlparse(uri)
    host = parsed_uri.hostname
    port = parsed_uri.port or (443 if parsed_uri.scheme == 'wss' else 80)

    reader, writer = await asyncio.open_connection(host, port)

    key = base64.b64encode(os.urandom(16)).decode('utf-8')

    request_headers = {
        "Host": host,
        "Connection": "Upgrade",
        "Upgrade": "websocket",
        "Sec-WebSocket-Version": "13",
        "Sec-WebSocket-Key": key,
    }
    request_headers.update(headers)

    request = f"GET {parsed_uri.path or '/'} HTTP/1.1\r\n"
    for key, value in request_headers.items():
        request += f"{key}: {value}\r\n"
    request += "\r\n"

    writer.write(request.encode('utf-8'))
    await writer.drain()

    status_code, response_headers = await read_response(reader)

    if status_code != 101:
        raise InvalidUpgrade(f"Handshake failed with status code {status_code}")

    return reader, writer
