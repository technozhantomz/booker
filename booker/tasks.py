from booker.config import Config
from booker.http.server import server_loop as http_server_loop


async def tasks_loop() -> None:
    config = Config()

    config.with_environment()

    await http_server_loop(config)
