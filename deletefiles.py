import configparser as ConfigParser
import shutil


def cleanup():

    config = ConfigParser.RawConfigParser()
    config.read("skeletonsuite.cfg")
    shutil.rmtree(config.get("locations", "output"), True)
