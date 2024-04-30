"""
Entrypoint for the Python Stack Example Application.
"""

import asyncio

from uvicorn import Server

from .application import Application


async def main() -> None:
    """
    Main entrypoint for the Python Stack Example Application.
    """
    # Create a new Application instance
    _app = Application()
    # Setup Uvicorn Server
    _server = Server(config=_app.build_uvicorn_config())
    # Run the server
    await _server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # silence the stack trace when the user interrupts the application
        # with a keyboard interrupt
        pass
