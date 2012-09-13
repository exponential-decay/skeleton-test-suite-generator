#skeleton test suite generator

import fmtxmlextractor
import os
import sys
import deletefiles
import re
import ConfigParser
import time

# read pronom export and forward to puid handlers
def readPronomExport(config):
	export_location = config.get('locations', 'xmlexport')

	for puids in ['fmt', 'x-fmt']:
		#go into loop to read each file in each folder and map data as required
		puid_xml_loc = export_location + '//' + puids
		if os.path.exists(puid_xml_loc):
			files_to_read = len(os.walk(puid_xml_loc).next()[2])		#not sure what [2] used for in this context
		
		for root, dirs, files in os.walk(puid_xml_loc):
			for file in files:
				file_path = root + "//" + file
				file_no = re.findall(r'\d+', file_path)[0] 	#create a file number based on integers in path
				fmtxmlextractor.handler(puids, [file_no, file_path])

def main():
	
	#time script execution time roughly...
	t0 = time.clock()
	
	config = ConfigParser.RawConfigParser()
	config.read('skeletonsuite.cfg')
	deletefiles.cleanup()
	readPronomExport(config)

	#print script execution time...
	print 'Skeleton suite generation time: ' + str(time.clock() - t0) + ' seconds.'

if __name__ == "__main__":
    main()