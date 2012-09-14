from urlparse import urlparse
import os
import sys
import signature2bytegenerator as sig2map
import ConfigParser
from io import BytesIO

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
		
		self.BOF=1	# enum-esque vars to help check already written sequences
		self.VAR=2
		self.EOF=3
		
		try:
			self.fillbyte = config.getint('runtime', 'fillbyte')
		except ValueError as (strerror):
			sys.stderr.write("Value Error: {0}. ".format(strerror) + "\n" + "Setting fillbyte to zero."  + '\n')
			self.fillbyte = 0
	
	# Write BOF sequence to file
	def write_header(self, pos, min, max, seq):
		
		self.detect_write_issues(self.BOF)
		
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
		self.bof_written = True
	
	# Write EOF sequence to file
	def write_footer(self, pos, min, max, seq):
	
		self.detect_write_issues(self.EOF)
	
		self.nt_file.seek(0,2)				# seek to end of file
		eof_sequence = sig2map.map_signature(0, seq, min, self.fillbyte)
		
		for x in eof_sequence:
			try:
				s = map(ord, x.decode('hex'))
				for y in s:
					self.nt_file.write(chr(y))
			except:
				sys.stderr.write("EOF Signature not mapped: " + seq + '\n\n')

		self.eof_written = True		
	
	# Write variable sequences to file	
	def write_var(self, pos, min, max, seq):
		
		self.detect_write_issues(self.VAR)
		
		self.nt_file.seek(self.boflen)
		var_sequence = sig2map.map_signature(10, seq, 10, self.fillbyte)		#padding sequence
		
		tmpread = False
		if self.eof_written == True:		# read eof into tmp and re-write
			tmpread = self.write_var_with_eof()
		
		for x in var_sequence:
			try:
				s = map(ord, x.decode('hex'))
				for y in s:
					self.nt_file.write(chr(y))
			except:
				sys.stderr.write("VAR Signature not mapped: " + seq + '\n\n')	
		
		if tmpread == True:
			self.nt_file.write(self.tmpbio.getvalue())
		
		self.var_written = True
	
	# Create a new file
	def write_file(self, puid, puid_no, sigID, value, ext):
		self.nt_string = self.newtriplesdir + puid + "-" + str(puid_no) + "-signature-id-" + sigID + '.' + ext
		self.puid_no = puid_no
		if os.path.exists(self.nt_string) == False:
			self.nt_file = open(self.nt_string, 'wb')

		self.puid_str = puid + '/' + str(self.puid_no)		
	
		# reset vars to ensure we know what sequences have been written
		self.bof_written = False
		self.var_written = False
		self.eof_written = False

	# we can attempt to write a var sequence with EOF already written
	# by creating a tmp location for the EOF data while we write the VAR out
	def write_var_with_eof(self):
		self.nt_file.close()
		self.nt_file = open(self.nt_string, 'r+b')	# consider default mode?
		self.nt_file.seek(self.boflen)
		self.tmpbio = BytesIO(self.nt_file.read())
		self.nt_file.seek(self.boflen)
		return True

	# The ordering of sequences in the PRONOM database may prevent the
	# successful generation of a skeleton file. Detect these issues and
	# provide feedback to users as a warning.
	def detect_write_issues(self, POS):
		
		error_str = "(" + self.puid_str + "): "
		
		if POS == self.BOF:
			if self.bof_written == True:
				sys.stderr.write("WARNING: " + error_str + "Attempting to write BOF with BOF written." + "\n")
		elif POS == self.EOF:
			if self.eof_written == True:
				sys.stderr.write("WARNING: " + error_str + "Attempting to write EOF with EOF written." + "\n")
		elif POS == self.VAR:
			if self.var_written == True:
				sys.stderr.write("WARNING: " + error_str + "Attempting to write VAR with VAR written." + "\n")
			if self.eof_written == True:
				sys.stderr.write("INFO:    " + error_str + "Attempting to write VAR with EOF written." + "\n")
