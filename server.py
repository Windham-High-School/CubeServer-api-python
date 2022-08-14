"""The API wrapper for sending data to the CubeServer server
See https://github.com/snorklerjoe/CubeServer-api-micropython for more info!
"""

import urequests as requests
from ubinascii import b2a_base64
import network
import machine

__all__ = [
    "DataClass",
    "DataPoint",
    "Temperature",
    "Humidity",
    "Pressure",
    "Intensity",
    "Text",
    "Server",
    "sta_if"
]


# Helpers:
def enum(**enums):
    return type('Enum', (), enums)

def basic_auth_str(user: str, pwd: str) -> str:
    """Encodes the username and password as per RFC7617 on Basic Auth"""
    return "Basic " + str(b2a_base64(f"{user}:{pwd}#").strip())

DEGREE_SIGN = u"\xb0"

# Global:
sta_if = None

# Data stuff:
DataClass = enum(
    TEMPERATURE = "temperature",
    HUMIDITY = "humidity",
    PRESSURE = "pressure",
    LIGHT_INTENSITY = "light intensity",
    COMMENT = "comment"
)

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
        return json.dumps(
            {
                "type": self.data_class.value,
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




# Main class:
class Server:
    """A class for the server"""
    def __init__(
        self,
        team_name: str,
        team_secret: str,
        server_addr: str = "https://192.168.252.1:8081",
        server_verify = "./trusted.pem", # :typing.Union[bool,str]
        auto_network: bool = True,  # Whether or not to automatically connect to the AP
        wifi_ssid: str = "CubeServer-API"
    ):
        """Initializes the connection for the API server
        Please provide the case-sensitive team name and the secret key
        If needed, the server's address can be defined with the server_addr
        kwarg
        If no other server_verify value is given as a kwarg, this looks for
        a file called trusted.pem. If the file exists or if a boolean value is
        given, the requests.Session().verify value will be set to this
        value."""

        # TODO: Localize this a bit more to improve RAM usage
        global sta_if
        if auto_network and not (sta_if and sta_if.isconnected()):
            sta_if = network.WLAN(network.STA_IF)
            sta_if.active(True)
            print(f"Connecting to {wifi_ssid}", end ="")
            sta_if.connect(wifi_ssid)
            while not sta_if.isconnected():
                print(".", end ="")
                machine.lightsleep(100)

            print()
            print("Connected!")


        self.authstr = basic_auth_str(team_name, team_secret)
        self.addr = server_addr
        self.verify = server_verify

        # Check status:
        if self.get_status() is None:
            raise IOError("Unable to communicate with the server.")

    def post(
        self,
        data #: Union[list[DataPoint], DataPoint]
    ) -> bool:
        """Posts a datapoint to the server, returns True on success"""
        if isinstance(data, list):  # Send multiple datapoints:
            return all(
                self.post(point) for point in data
            )
        # Just send one datapoint:
        response = requests.post(
            f"{self.addr}/data", data={"data":data.dumps()},
            headers={'Authorization': self.authstr}
        )
        if response.status_code != 201:
            return False
        return True

    def get_status(self):
        response = requests.get(
            f"{self.addr}/status",
            headers={'Authorization': self.authstr}
        )
        if response.status_code in [401, 403]:
            print("Invalid authorization config. Check the team name and secret.")
        if response.status_code == 200:
            return response.json()
        return None
