"""
Brinkpy CLI - Command-line interface for reliability analysis and design using the Brinkpy API.
Copyright (c) 2025 Cesar Carrasco. All rights reserved.
"""

__version__ = "0.1.0"
__author__ = "Cesar Carrasco"
__email__ = "reliafy.app@gmail.com"  # Optional
__description__ = "Command-line interface for reliability analysis and design using the Brinkpy API"

# You can also expose main components if needed
from brinkpy.brinkpy import app as main

__all__ = ["main", "__version__"]
