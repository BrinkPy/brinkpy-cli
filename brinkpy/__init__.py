"""
Brinkpy CLI - Command-line interface for reliability analysis and design using the Brinkpy API.

Why "Brinkpy"? Every reliability problem has an edge: the limit-state surface where
safe becomes failed. The reliability index measures how far you stand from that brink.
FORM and SORM find the point where you are most likely to cross it, design keeps you a
set distance back, and simulation samples both sides to count how often you go over.
The "py" is for Python.

Copyright (c) 2025 Cesar Carrasco. All rights reserved.
"""

__version__ = "0.1.0"
__author__ = "Cesar Carrasco"
__email__ = "brinkpy.app@gmail.com"  # Optional
__description__ = "Command-line interface for reliability analysis and design using the Brinkpy API"

# You can also expose main components if needed
from brinkpy.brinkpy import app as main

__all__ = ["main", "__version__"]
