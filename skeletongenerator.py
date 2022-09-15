# skeleton test suite generator

import argparse
import configparser as ConfigParser
import os
import re
import sys
import time

import deletefiles
import fmtxmlextractor


# read pronom export and forward to puid handlers
def readPronomExport(config):
    export_location = config.get("locations", "xmlexport")

    for puids in ["fmt", "x-fmt"]:
        # go into loop to read each file in each folder and map data as required
        puid_xml_loc = export_location + "//" + puids
        for root, dirs, files in os.walk(puid_xml_loc):
            for file in files:
                file_path = root + "//" + file
                file_no = re.findall(r"\d+", file_path)[
                    0
                ]  # create a file number based on integers in path
                fmtxmlextractor.handler(puids, [file_no, file_path])


def parseCommandLine():
    parser = argparse.ArgumentParser(
        description="Tool for the automated generation of digital objects based on the digital signatures documented in the PRONOM database maintained by The National Archives, UK."
    )
    parser.add_argument(
        "--version",
        help="Display the version number of the tool",
        action="version",
        version="%(prog)s v0.2-BETA",
    )
    _ = parser.parse_args()


def main():

    parseCommandLine()

    # time script execution time roughly...
    # TODO: time.process_time() may also be appropriate.
    t0 = time.perf_counter()

    config = ConfigParser.RawConfigParser()
    config.read("skeletonsuite.cfg")
    deletefiles.cleanup()
    readPronomExport(config)

    # print script execution time...
    sys.stdout.write(
        "Skeleton suite generation time:    "
        + str(time.perf_counter() - t0)
        + "s"
        + "\n"
    )

    # print script stats
    stats = fmtxmlextractor.get_stats()
    for value in stats:
        sys.stdout.write(value + str(stats[value]) + "\n")


if __name__ == "__main__":
    main()
