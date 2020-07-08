import asyncio
import logging

from booker.tasks import tasks_loop


logging.basicConfig(level=logging.DEBUG)
asyncio.run(tasks_loop())
