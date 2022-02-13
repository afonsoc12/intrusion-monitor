#!/usr/bin/env python3

# Execute with
# $ python intrusion_monitor/__main__.py
# $ python -m intrusion_monitor

import sys

if __package__ is None and not hasattr(sys, "frozen"):
    # Direct call of __main__.py
    import os.path

    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

import intrusion_monitor

if __name__ == "__main__":
    intrusion_monitor.main()
