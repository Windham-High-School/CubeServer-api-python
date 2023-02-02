# CubeServer-api-circuitpython

[![Maintainability](https://api.codeclimate.com/v1/badges/0ed05bb07ca3c9678002/maintainability)](https://codeclimate.com/github/snorklerjoe/CubeServer-api-circuitpython/maintainability)

The CircuitPython/CPython version of the data API wrapper for a high-school STEM competition

This is implemented for both CPython (it is assumed the computer is already connected to the access point for this use-case) and CircuitPython (for microcontrollers).

# Example code:
``` Python
from servercom import Connection, Text

print("Connecting to the server...")
connection = Connection()
print("Connected!")

connection.post(Text("Test from CircuitPython!"))

print("Getting status:")
print(connection.get_status())
```
-------------------------------------------------------------------


## Limitations & Considerations

- This library disables concurrent write protection-
If your code stores something to a file, be careful when writing to it while the board is plugged in to avoid corruption!

### Testing Status:
| MCU         | Description |
| ----------- | ----------- |
| ESP32       | Works       |
| ESP8266     | Incompatible|
| Raspi Pico W| Untested    |

The ESP8266 is currently incompatible with this micropython library due to lack of memory resources for handling the TLS handshake.
To use the ESP8266, please use the Arduino C wrapper.
