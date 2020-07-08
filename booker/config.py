from os import getenv

from marshmallow.exceptions import (
    ValidationError as MarshmallowSchemaValidationError
)
from marshmallow_dataclass import dataclass

from booker.dto import DTOInvalidType, DataTransferClass


@dataclass
class Config(DataTransferClass):
    http_host: str = '127.0.0.1'
    http_port: int = 8080


    def with_environment(self) -> None:
        schema = type(self).Schema()

        try:
            updater = schema.load({
                'http_host': getenv('HTTP_HOST'),
                'http_port': getenv('HTTP_PORT')
            })
        except MarshmallowSchemaValidationError as exception:
            logging.debug(exception)

            raise DTOInvalidType(f'Invalid payload type: {exception}')

        self.update(updater)
