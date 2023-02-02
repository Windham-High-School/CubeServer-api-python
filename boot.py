# OFFICIAL CubeServer Helper Code - DO NOT REMOVE!
""" This file is run on hard resets and during code updates.
    Copyright (c) 2023 Joseph R. Freeston
"""

import storage

print("Mounting storage with concurrent write protection off.")
storage.remount("/", False, disable_concurrent_write_protection=True)

