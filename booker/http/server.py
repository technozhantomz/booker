import asyncio
import logging

from aiohttp.web import GracefulExit, Application, AppRunner, TCPSite

from booker.config import Config
from booker.http.handlers import routes


async def server_loop(config: Config) -> None:
    app = Application()

    app.add_routes(routes)

    runner = AppRunner(app)

    await runner.setup()

    try:
        site = TCPSite(runner, config.http_host, config.http_port)

        await site.start()

        logging.info('HTTP server is running.')

        while True:
            await asyncio.sleep(3600)
    except (GracefulExit, KeyboardInterrupt):
        ...
    finally:
        await runner.cleanup()
        logging.info('HTTP service has stopped.')
