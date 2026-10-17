#!/usr/bin/env python3
"""Shortcut launcher, so `python play.py` works without `-m`."""
import sys

from kbc.cli import main

if __name__ == "__main__":
    sys.exit(main())
