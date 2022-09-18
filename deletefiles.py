"""Cleans up after the skeleton suite generator."""

import configparser as ConfigParser
import shutil


def cleanup():
    """Cleanup function for the skeleton suite generator."""
    config = ConfigParser.RawConfigParser()
    config.read("skeletonsuite.cfg")
    shutil.rmtree(config.get("locations", "output"), True)
