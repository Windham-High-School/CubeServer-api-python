"""Example code"""

from server import CubeServer, Text

print("Connecting to the server...")
connection = CubeServer()
print("Connected!")

connection.post(Text("Test from CircuitPython!"))

print("Getting status:")
print(connection.get_status())
