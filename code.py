"""Example code"""

from servercom import Connection, Text

# Connect to server:
print("Connecting to the server...")
connection = Connection()
print("Connected!")

# Sync time:
connection.sync_time()

# If none, post Hello World:
connection.post(Text("Hello World!"))

# Check for code updates from the server:
connection.code_update()

# Get status:
print("Getting status:")
print(connection.get_status())
