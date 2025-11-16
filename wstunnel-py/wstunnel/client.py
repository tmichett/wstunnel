import asyncio
import websockets
import logging
from .tcp_tunnel import create_tcp_tunnel
from .ws_client import WsClient
from .udp_tunnel import create_udp_tunnel
from .socks5_tunnel import create_socks5_tunnel
from .http_proxy_tunnel import create_http_proxy_tunnel

async def run_client(args):
    client = WsClient(args)

    if args.local_to_remote:
        tasks = []
        for tunnel in args.local_to_remote:
            local_protocol, local_addr, remote_protocol, remote_addr = tunnel.split(":")
            local_host, local_port = local_addr.split("/")
            remote_host, remote_port = remote_addr.split("/")

            if local_protocol == "tcp":
                tasks.append(
                    create_tcp_tunnel(
                        local_host,
                        int(local_port),
                        remote_host,
                        int(remote_port),
                        client,
                    )
                )
            elif local_protocol == "udp":
                tasks.append(
                    create_udp_tunnel(
                        local_host,
                        int(local_port),
                        remote_host,
                        int(remote_port),
                        client,
                    )
                )
            elif local_protocol == "socks5":
                tasks.append(
                    create_socks5_tunnel(
                        local_host,
                        int(local_port),
                        client,
                    )
                )
            elif local_protocol == "http-proxy":
                tasks.append(
                    create_http_proxy_tunnel(
                        local_host,
                        int(local_port),
                        client,
                    )
                )
        await asyncio.gather(*tasks)
