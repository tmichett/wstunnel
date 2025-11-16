import asyncio
import click
from . import run_client, run_server
from .config import Client, Server

@click.group()
@click.option('--log-lvl', default='INFO', help='Log level')
@click.pass_context
def main(ctx, log_lvl):
    """
    Python implementation of wstunnel.
    """
    ctx.ensure_object(dict)
    ctx.obj['LOG_LVL'] = log_lvl

@main.command()
@click.argument('url')
@click.option('-L', '--local-to-remote', multiple=True, help='Listen on local and forwards traffic from remote.')
@click.option('-R', '--remote-to-local', multiple=True, help='Listen on remote and forwards traffic from local.')
@click.option('-p', '--http-proxy', help='If set, will use this http proxy to connect to the server')
@click.pass_context
def client(ctx, url, local_to_remote, remote_to_local, http_proxy):
    """
    Run the wstunnel client.
    """
    config = Client(
        remote_addr=url,
        local_to_remote=local_to_remote,
        remote_to_local=remote_to_local,
        http_proxy=http_proxy,
        log_lvl=ctx.obj['LOG_LVL']
    )
    asyncio.run(run_client(config))

@main.command()
@click.argument('url')
@click.option('--restrict-to', multiple=True, help='Server will only accept connection from the specified tunnel information.')
@click.pass_context
def server(ctx, url, restrict_to):
    """
    Run the wstunnel server.
    """
    config = Server(
        remote_addr=url,
        restrict_to=restrict_to,
        log_lvl=ctx.obj['LOG_LVL']
    )
    asyncio.run(run_server(config))


if __name__ == '__main__':
    main()
