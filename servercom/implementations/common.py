"""Helpers, interfaces, etc. common to ALL implementations"""

# Try to import configuration file
try:
    import client_config
except ImportError:
    pass

from collections import namedtuple
from json import dumps

# Constants:
DEGREE_SIGN = u"\xb0"


GameStatus = namedtuple("GameStatus",
    ['time',
    'score',
    'CubeServer_version']
)

HTTPResponse = namedtuple("HTTPResponse",
    ['code', 'body']
)

def conf_if_exists(key: str):
    """Returns the config value if client_config is imported, else None"""
    if 'client_config' not in globals():
        return None
    return getattr(client_config, key)

class ConnectionConfig:
    """The configuration of the connection to the server"""
    TIMEOUT: int = 10
    if 'client_config' in globals():
        AP_SSID: str = client_config.CONF_AP_SSID
        AP_PASSWORD: str = client_config.CONF_AP_PASSWORD if hasattr(client_config, "CONF_AP_PASSWORD") else ""
        API_HOST: str = client_config.CONF_API_HOST
        API_PORT: int = client_config.API_PORT
    else:
        AP_SSID: str = "CubeServer-API"
        AP_PASSWORD: str = ""
        API_HOST: str = "api.local"
        API_PORT: int = 8081

CUBESERVER_DEFAULT_CONFIG = ConnectionConfig()

class Email:
    """Holds an email to be sent to the team"""

    def __init__(self, subject, message) -> None:
        self.subject = subject
        self.message = message

    def dumps(self) -> str:
        return dumps(
            {
                'subject': self.subject,
                'message': self.message
            }
        )
