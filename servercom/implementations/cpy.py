"""CPython implementation of the CubeServer API Wrapper Library"""

from .common import *

import ssl
import socket
from gc import collect
from collections import namedtuple
from binascii import b2a_base64
from errno import EAGAIN
from json import loads, dumps
from urllib.parse import quote_plus
from enum import Enum
from typing import Union


# Helpers:
class DataClass(str, Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    LIGHT_INTENSITY = "light intensity"
    COMMENT = "comment"
    BATTERY = "remaining battery"

class DataPoint():
    """A class for storing and handling datapoints"""

    @staticmethod
    @property
    #@abstractmethod
    def UNIT() -> str:
        """A standard string representation of the unit for this datapoint"""

    def __init__(self, data_class: DataClass, value: Union[int, float, str]):
        """Initializes a piece of data to send to the server"""
        self.data_class = data_class
        self.value = value

    def dumps(self) -> str:
        """Dumps a JSON string out that the server will (hopefully) accept"""
        return dumps(
            {
                "type": self.data_class,
                "value": self.value
            }
        )

    def __str__(self) -> str:
        return f"{self.value} {self.UNIT}"

class Temperature(DataPoint):
    """A class for DataPoints that store temperature values"""
    UNIT = f"{DEGREE_SIGN}F"
    def __init__(self, value):
        super().__init__(DataClass.TEMPERATURE, value)

class Humidity(DataPoint):
    """A class for DataPoints that store humidity values"""
    UNIT = "%"
    def __init__(self, value):
        super().__init__(DataClass.HUMIDITY, value)

class Pressure(DataPoint):
    """A class for DataPoints that store barometric pressure values"""
    UNIT="inHg"
    def __init__(self, value):
        super().__init__(DataClass.PRESSURE, value)

class Intensity(DataPoint):
    """A class for DataPoints that store light intensity values"""
    UNIT="lux"
    def __init__(self, value):
        super().__init__(DataClass.LIGHT_INTENSITY, value)

class Text(DataPoint):
    """A class reserved for DataPoints that are intended as a text comment"""
    UNIT=""  # No unit for regular strings of text
    def __init__(self, value: str):
        super().__init__(DataClass.COMMENT, value)

class BatteryLevel(DataPoint):
    """A class reserved for DataPoints that are intended as an indication of battery level"""
    UNIT="%"  # No unit for regular strings of text
    def __init__(self, value: int):
        super().__init__(DataClass.BATTERY, value)

class ConnectionError(Exception):
    """Indicates an issue with the server connection"""

class AuthorizationError(ConnectionError):
    """Indicates an issue with the team credentials"""

def basic_auth_str(user: str, pwd: str) -> str:
    """Encodes the username and password as per RFC7617 on Basic Auth"""
    return b2a_base64(f"{user}:{pwd}".encode()).strip().decode("utf-8")

def urlencode(stuff: str) -> str:
    """URL-encodes a string"""
    return quote_plus(stuff)

class Connection:
    """A class for connecting to the server"""

    def __init__(
        self,
        team_name: str = conf_if_exists('TEAM_NAME'),
        team_secret: str = conf_if_exists('TEAM_SECRET'),
        server_cert: str = conf_if_exists('SERVER_CERT'),
        conf = CUBESERVER_DEFAULT_CONFIG,
        verbose: bool = False,
        _force: bool = False,
        _hostname: str = ""
    ):
        """Initializes the connection to the server"""

        # Check parameters:
        if not _force and (
            team_name is None or \
            team_secret is None or \
            server_cert is None
           ) or \
           not isinstance(conf, ConnectionConfig):
            raise TypeError("Bad parameters or client config")

        if _hostname:
            print(
                f"The hostname {_hostname} will not take effect. "
                "This parameter does not apply to the CPython implementation."
            )

        self.team_name = team_name
        self.team_secret = team_secret
        self.server_cert = server_cert
        self.conf = conf
        self.v = verbose

        if self.v:
            print("Obtaining and configuring SSL context...")
        self.context = ssl.create_default_context()
        self.context.check_hostname = False
        if self.v:
            print("Installing server CA certificate for server verification")
        self.context.load_verify_locations(cadata=server_cert)

    def connect_wifi(self) -> None:
        """Exists for compatibility with the CircuitPython implementation
        Creates the wifi connection to the access point"""
        pass

    def close_wifi(self) -> None:
        """Exists for compatibility with the CircuitPython implementation
        Disconnects from the access point and shuts off the radio"""
        pass

    def connect_socket(self) -> None:
        """Creates a socket connection to the server"""
        if self.v:
            print("Connecting the socket...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.wrapped_socket = self.context.wrap_socket(self.sock)
        self.wrapped_socket.settimeout(self.conf.TIMEOUT)
        self.wrapped_socket.connect((self.conf.API_HOST, self.conf.API_PORT))

    def close_socket(self) -> None:
        """Closes the socket connection and cleans up"""
        if self.v:
            print("Closing the socket...")
        if hasattr(self, 'wrapped_socket'):
            self.wrapped_socket.close()
            del self.wrapped_socket
        if hasattr(self, 'sock'):
            self.sock.close()
            del self.sock

    @property
    def radio(self):
        """Exists for compatibility with the CircuitPython implementation"""
        return None

    def rx_bytes(self) -> bytes:
        response = b""
        while True:
            buf = bytearray(256)
            try:
                recvd = self.wrapped_socket.recv_into(buf, 256)
            except OSError as e:
                if e.errno == EAGAIN:
                    recvd = 0
                else:
                    raise
            response += buf
            del buf
            collect()
            if self.v:
                print(f"Received {recvd} bytes")
            if recvd == 0:
                del recvd
                collect()
                break
            del recvd
            collect()
        return response

    def _do_request(
        self,
        method: str,
        path: str,
        body: str = None,
        content_type: str = None,
        headers: list[str] = []
    ) -> str:
        if self.team_name is None:
            raise TypeError("This connection instance is not configured properly for making REST requests.")

        if self.v:
            print(f"Making {method} request to {path}...")

        exception: Exception = None
        response = None
        try:
            # Create the socket:
            self.connect_socket()

            # Generate request text:
            auth_str = basic_auth_str(self.team_name, self.team_secret)
            req_text = str(
                f"{method} {path} HTTP/1.1\r\n" +
                "Host: api.local\r\n" +
                "Connection: close\r\n" +
                f"Authorization: Basic {auth_str}\r\n" +
                '\r\n'.join(headers)
            )
            del auth_str
            collect()
            if body is not None:
                if content_type is None:
                    raise TypeError(
                        "The keyword argument content_type must be provided"
                        " to accompany the request body."
                    )
                req_text += str(
                    f"\r\nContent-Type: {content_type}\r\n" +
                    f"Content-Length: {len(body)}\r\n" +
                    f"\r\n{body}\r\n"
                )
            req_text += '\r\n'

            if self.v:
                print("Sending request...")
                print(req_text)
            sent = 0
            req = req_text.encode()
            del req_text
            collect()
            while sent < len(req):
                sent += self.wrapped_socket.send(req[sent:])
                if self.v:
                    print(f"Sent {sent}/{len(req)} bytes")
            del sent
            collect()
            del req
            collect()
            if self.v:
                print("Receiving response...")
            self.wrapped_socket.setblocking(True)
            response = self.rx_bytes()
        except Exception as e:
            if self.v:
                print("An error occurred. Cleaning up...")
            exception = e
        finally:
            # Close the socket:
            self.close_socket()
        if exception is not None:
            raise exception
        collect()
        return response.decode().replace('\x00', '')

    def parse_response(
        self,
        response: str
    ) -> HTTPResponse:
        """Parses an HTTP response into a tuple of the useful stuff like so:
        (response_code: int, response_body: str)
        """
        if len(response) == 0:
            return HTTPResponse(-1, "")
        try:
            response_code = int(response.split(' ')[1].strip())
            response_body = response.split('\r\n\r\n')[1].strip()
            collect()
        except IndexError:
            collect()
            return HTTPResponse(-1, "")    
        return HTTPResponse(response_code, response_body)

    def request_once(
        self,
        method: str,
        path: str,
        body: str = None,
        content_type: str = None,
        headers: list[str] = []
    ) -> HTTPResponse:
        """Makes an HTTP request to the server, trying only once"""
        resp = self.parse_response(
            self._do_request(method, path, body, content_type, headers)
        )
        collect()
        if self.v:
            print(f"Response: {resp}")
        if resp.code == 401:
            raise AuthorizationError("The server did not trust the authenticity of this request.")
        elif resp.code == -1:
            raise ValueError("Got an unexpected response from the server")
        elif resp.code // 100 != 2:
            raise ConnectionError(f"The server returned invalid HTTP response code {resp.code}")
        collect()
        return resp
    
    def request(
        self,
        method: str,
        path: str,
        body: str = None,
        content_type: str = None,
        headers: list[str] = [],
        attempts: int = 10
    ) -> HTTPResponse:
        """Makes an HTTP request in the given number of max attempts"""
        last_error: Exception = None
        for _ in range(attempts):
            try:
                return self.request_once(method, path, body, content_type, headers)
            except (ValueError, ConnectionError) as e:
                last_error = e
        raise last_error

    def get_status(self) -> GameStatus:
        resp = self.request('GET', '/status')
        resp_json = loads(resp[1])
        return GameStatus(resp_json['unix_time'], resp_json['status']['score'], resp_json['status']['strikes'])

    def post(self, point: DataPoint) -> bool:
        return self.request(
            'POST',
            '/data',
            point.dumps(),
            content_type = 'application/json',
            headers=['User-Agent: CPython, dude!']
        ).code == 201
    def email(self, msg: Email) -> bool:
        return self.request(
            'POST',
            '/email',
            msg.dumps(),
            content_type = 'application/json',
            headers=['User-Agent: CPython, dude!']
        ).code == 201
    def code_update(reset=True):
        pass
    def __exit__(self):
        if self.v:
            print("Closing the server connection-")
        self.close_socket()
        self.close_wifi()
