"""

!!! the drive helper is NOT tested properly, since that is pretty difficult with the api!

This file attempts to test as much around the actual api as possible, but that's very limited.
"""

from src.verysimpletransformers import drive


def test_drive():
    token = "---" # obviously invalid token

    first = drive.DriveSingleton(token)
    second = drive.DriveSingleton(token)

    # test if singleton is actually the same object
    assert first is second
