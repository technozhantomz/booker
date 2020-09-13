import pytest
from booker_api.config import Config


def test_config():
    c = Config()
    assert c.http_port == 8080


def test_config_with_env():
    c = Config()
    c.with_env()
    print(c.db_port, c.http_port)
    assert c.db_port != Config.http_port
    assert c.http_port != Config.http_port
