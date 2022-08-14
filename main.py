"""An example usage of the library in server.py"""

from server import Server, Temperature

connection = Server("The Yodlers", "89c84")

connection.post(Temperature(100.0))

