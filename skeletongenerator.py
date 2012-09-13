#puid type mapping script...

import fmtxmlextractor
import os
import sys
import deletefiles
import re

deletefiles.cleanup()

#test file exists, if it doesn't we need to increment x
#and ensure for each file that doesn't exist we read the
#next one that does for all files...
def test_file(file_no, file_path):

	new_file_path = file_path + str(file_no) + '.xml'

	if os.path.exists(new_file_path) == False:
		new_file_no = file_no + 1

		#recurse until we have correct value. odd code, return is call to
		#function, not sure why python does this...
		return test_file(new_file_no, file_path)	
	else:
		#return a file number that exists, return the file path for that file
		return [file_no, new_file_path]


#############################################################
# Main
# Main thread of execution...
#############################################################
export_location = 'pronom_export'

for puids in ['fmt', 'x-fmt']:
	
	files_to_read = 0

	#go into loop to read each file in each folder and map data as required
	puid_xml_loc = export_location + '//' + puids
	if os.path.exists(puid_xml_loc):
		files_to_read = len(os.walk(puid_xml_loc).next()[2])		#not sure what [2] used for in this context
	
	for root, dirs, files in os.walk(puid_xml_loc):
		for file in files:
			file_path = root + "//" + file
			file_no = re.findall(r'\d+', file_path)[0] 	#create a file number based on integers in path
			fmtxmlextractor.handler(puids, [file_no, file_path])
