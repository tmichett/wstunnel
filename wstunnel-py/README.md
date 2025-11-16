# Wstunnel in Python

This is a Python port of the original Rust `wstunnel` application. It provides the same core functionality, allowing you to tunnel TCP and UDP traffic over WebSockets.

## How to Build

Install `uv` https://github.com/astral-sh/uv

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

and run those commands at the root of the project

```
uv venv
source .venv/bin/activate
uv pip install -e .
wstunnel --help
```
