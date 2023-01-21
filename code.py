"""Example code"""

from servercom import Connection, Text

print("Connecting to the server...")
connection = Connection()
print("Connected!")

connection.post(Text("Test from CircuitPython!"))

print("Getting status:")
print(connection.get_status())
