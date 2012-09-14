from urlparse import urlparse
import os
import sys
import signature2bytegenerator as sig2map
import ConfigParser

class FileWriter:

	# Class constructor
	def __init__(self, puid_type):
	
		config = ConfigParser.RawConfigParser()
		config.read('skeletonsuite.cfg') 

		self.newtriplesdir = os.getcwd() + "//" + config.get('locations', 'output') + "//" + puid_type + '//'

		if os.path.exists(self.newtriplesdir) == False:
			try:
				os.makedirs(self.newtriplesdir)
			except OSError as (errno, strerror):
				sys.stderr.write("OS error({0}): {1}".format(errno, strerror) + '\n')
		
		#variables to hold details about individual triple files
		self.nt_file = 0		#to hold file pointer
		self.puid_no = 0		#to hold the puid number we're looking at
		self.nt_string = 0 	#triple file path...
		self.boflen = 0		#length of the bof sequence after writing
		
		try:
			self.fillbyte = config.getint('runtime', 'fillbyte')
		except ValueError as (strerror):
			sys.stderr.write("Value Error: {0}. ".format(strerror) + "\n" + "Setting fillbyte to zero."  + '\n')
			self.fillbyte = 0
	
	# Write BOF sequence to file
	def write_header(self, pos, min, max, seq):
		
		self.nt_file.seek(0)	
		bof_sequence = sig2map.map_signature(min, seq, 0, self.fillbyte)
		
		for x in bof_sequence:
			try:
				s = map(ord, x.decode('hex'))
				for y in s:
					self.nt_file.write(chr(y))
			except:
				sys.stderr.write("BOF Signature not mapped: " + seq + '\n\n')

		self.boflen = self.nt_file.tell()
	
	# Write EOF sequence to file
	def write_footer(self, pos, min, max, seq):
	
		self.nt_file.seek(0,2)				# seek to end of file
		eof_sequence = sig2map.map_signature(0, seq, min, self.fillbyte)
		
		for x in eof_sequence:
			try:
				s = map(ord, x.decode('hex'))
				for y in s:
					self.nt_file.write(chr(y))
			except:
				sys.stderr.write("EOF Signature not mapped: " + seq + '\n\n')		
		
	# Write variable sequences to file	
	def write_var(self, pos, min, max, seq):
		
		self.nt_file.seek(self.boflen)
		var_sequence = sig2map.map_signature(10, seq, 10, self.fillbyte)		#padding sequence
		
		for x in var_sequence:
			try:
				s = map(ord, x.decode('hex'))
				for y in s:
					self.nt_file.write(chr(y))
			except:
				sys.stderr.write("VAR Signature not mapped: " + seq + '\n\n')	
	
	# Create a new file
	def write_file(self, puid, puid_no, sigID, value, ext):
		self.nt_string = self.newtriplesdir + puid + "-" + str(puid_no) + "-signature-id-" + sigID + '.' + ext
		self.puid_no = puid_no
		if os.path.exists(self.nt_string) == False:
			self.nt_file = open(self.nt_string, 'wb')
