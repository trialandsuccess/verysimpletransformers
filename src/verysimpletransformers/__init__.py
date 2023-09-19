"""
This file exposes 'app' to the module.
"""

# SPDX-FileCopyrightText: 2023-present Robin van der Noord <robinvandernoord@gmail.com>
#
# SPDX-License-Identifier: MIT
from rich import print

from .cli import app

__all__ = ["app", "print"]
