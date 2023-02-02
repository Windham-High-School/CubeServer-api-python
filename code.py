"""Example code"""

from servercom import Connection, Text

# Connect to server:
print("Connecting to the server...")
connection = Connection()
print("Connected!")

# Turn off WiFi to save power:
connection.close_wifi()

# Reconnect WiFi when ready:
connection.connect_wifi()

# Check for code updates from the server:
connection.code_update()

# If none, post Hello World:
connection.post(Text("Hello World!"))

# Get status:
print("Getting status:")
print(connection.get_status())
