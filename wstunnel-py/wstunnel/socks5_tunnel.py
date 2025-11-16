import asyncio

async def handle_socks5_connect(reader, writer, ws_client):
    data = await reader.read(1024)
    # Version and number of methods
    if data[0] != 5:
        return
    
    # Choose no authentication
    writer.write(b'\x05\x00')
    await writer.drain()

    data = await reader.read(1024)
    # version, command, reserved, address type
    if data[1] != 1: # CONNECT
        return
    
    address_type = data[3]
    if address_type == 1: # IPv4
        remote_host = ".".join(map(str, data[4:8]))
        remote_port = int.from_bytes(data[8:10], 'big')
    elif address_type == 3: # Domain name
        domain_length = data[4]
        remote_host = data[5:5+domain_length].decode()
        remote_port = int.from_bytes(data[5+domain_length:7+domain_length], 'big')
    elif address_type == 4: # IPv6
        remote_host = ":".join(map(lambda x: x.hex(), data[4:20]))
        remote_port = int.from_bytes(data[20:22], 'big')
    else:
        return

    ws_reader, ws_writer = await ws_client.open_connection(remote_host, remote_port, "tcp")

    writer.write(b'\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00')
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


async def handle_socks5_tunnel(reader, writer, ws_client):
    await handle_socks5_connect(reader, writer, ws_client)


async def create_socks5_tunnel(local_host, local_port, ws_client):
    server = await asyncio.start_server(
        lambda r, w: handle_socks5_tunnel(r, w, ws_client),
        local_host,
        local_port
    )
    async with server:
        await server.serve_forever()
