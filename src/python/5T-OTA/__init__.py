#!/usr/bin/env python3

"""
5T-OTA Module

This module implements a 5-transistor Operational Transconductance Amplifier (OTA) design
consisting of:
- PMOS current mirror (2 transistors) for biasing
- NMOS differential pair (2 transistors) for input stage
- Additional tail current source (if needed)

The design is optimized for the GF180MCU process.
"""

from .five_t_ota import FiveTOTA, OTAConfig

__all__ = ['FiveTOTA', 'OTAConfig']
