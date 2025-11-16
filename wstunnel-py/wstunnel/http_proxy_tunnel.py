import asyncio

async def handle_http_connect(reader, writer, ws_client):
    data = await reader.read(1024)
    request_line = data.split(b'\r\n')[0]
    method, a, _ = request_line.split(b' ')

    if method != b'CONNECT':
        return

    address = a.decode()
    remote_host, remote_port = address.split(':')

    ws_reader, ws_writer = await ws_client.open_connection(remote_host, int(remote_port), "tcp")

    writer.write(b'HTTP/1.1 200 OK\r\n\r\n')
    await writer.drain()

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


async def handle_http_proxy_tunnel(reader, writer, ws_client):
    await handle_http_connect(reader, writer, ws_client)


async def create_http_proxy_tunnel(local_host, local_port, ws_client):
    server = await asyncio.start_server(
        lambda r, w: handle_http_proxy_tunnel(r, w, ws_client),
        local_host,
        local_port
    )
    async with server:
        await server.serve_forever()
