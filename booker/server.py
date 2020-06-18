import logging

from aiohttp.web import Application, run_app


async def init() -> Application:
    logging.basicConfig(level=logging.DEBUG)

    logging.info('Run backend')

    app = Application()

    return app


def main() -> None:
    run_app(init(), host='127.0.0.1', port=8080)
