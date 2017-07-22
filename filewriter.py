from urlparse import urlparse
import os
import sys
import string
import signature2bytegenerator
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
		self.sig2map = signature2bytegenerator.Sig2ByteGenerator()	#TODO: New instance or not?
		
		grt1 = '' #"Attempting to correct: offset > current BOF" 
		grt2 = '' #"file pointer.."
		eq2  = '' #"Attempting to correct: offset == zero so" 
		eq3  = '' #"writing after..."
		
		self.detect_write_issues(self.BOF)
		bof_sequence = ''
		if self.bof_written == True:
			if int(min) > int(self.boflen):
				sys.stderr.write(string.ljust(" ", 22, ' ') + string.rjust(grt1, 20, ' ') + '\n')
				sys.stderr.write(string.ljust(" ", 16, ' ') + string.rjust(grt2, 20, ' ') + '\n')
				self.nt_file.seek(self.boflen)
				mint = int(min) - int(self.boflen)
				bof_sequence = self.sig2map.map_signature(mint, seq, 0, self.fillbyte)
			elif int(min) == 0:	# if second sequence is zero may be error in PRONOM
										# so write after BOF to not overwrite anything
				sys.stderr.write(string.ljust(" ", 22, ' ') + string.rjust(eq2, 20, ' ') + '\n')
				sys.stderr.write(string.ljust(" ", 18, ' ') + string.rjust(eq3, 20, ' ') + '\n')
				self.nt_file.seek(self.boflen)	
				bof_sequence = self.sig2map.map_signature(min, seq, 0, self.fillbyte)
		else:
			self.nt_file.seek(0)	
			bof_sequence = self.sig2map.map_signature(min, seq, 0, self.fillbyte)
			
		tmpread = False
		if self.eof_written == True:		# read eof into tmp and re-write
			tmpread = self.write_seq_with_eof()

		for x in bof_sequence:
			try:
				s = map(ord, x.decode('hex'))
				for y in s:
					self.nt_file.write(chr(y))
			except TypeError as e:
				print e
			#	sys.stderr.write("BOF Signature not mapped: " + seq + '\n\n')
			#	print x

		self.boflen = self.nt_file.tell()
		self.bof_written = True

		if tmpread == True:
			self.nt_file.write(self.tmpbio.getvalue())
	
	# Write EOF sequence to file
	def write_footer(self, pos, min, max, seq):
		self.sig2map = signature2bytegenerator.Sig2ByteGenerator()	#TODO: New instance or not?
		self.detect_write_issues(self.EOF)
	
		self.nt_file.seek(0,2)				# seek to end of file
		eof_sequence = self.sig2map.map_signature(0, seq, min, self.fillbyte)
		
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
		self.sig2map = signature2bytegenerator.Sig2ByteGenerator()	#TODO: New instance or not?
		self.detect_write_issues(self.VAR)
		
		if self.var_written == False:
			self.var_pos = self.boflen
			self.var_written = True

		self.nt_file.seek(self.var_pos)
		var_sequence = self.sig2map.map_signature(min, seq, max, self.fillbyte)		#padding sequence
		
		tmpread = False
		if self.eof_written == True:		# read eof into tmp and re-write
			tmpread = self.write_seq_with_eof()
		
		for x in var_sequence:
			try:
				s = map(ord, x.decode('hex'))
				for y in s:
					self.nt_file.write(chr(y))
			except:
				sys.stderr.write("VAR Signature not mapped: " + seq + '\n\n')	
		
		if tmpread == True:
			self.nt_file.write(self.tmpbio.getvalue())
		
		self.var_pos = self.nt_file.tell()
		self.var_written = True
	
	# Create a new file
	def write_file(self, puid, puid_no, sigID, value, ext):
		self.nt_string = self.newtriplesdir + puid + "-" + str(puid_no) + "-signature-id-" + sigID + '.' + ext
		self.puid_no = puid_no
		if os.path.exists(self.nt_string) == False:
			self.nt_file = open(self.nt_string, 'wb')

		self.puid_str = puid + '/' + str(self.puid_no)		
	
		# Vars to ensure we know what sequences have been written
		self.bof_written = False
		self.var_written = False
		self.eof_written = False
		self.boflen = 0				#init or here, no problem

	# we can attempt to write a var or BOF sequence with EOF already written
	# by creating a tmp location for the EOF data while we write the VAR out
	def write_seq_with_eof(self):
		self.nt_file.close()
		self.nt_file = open(self.nt_string, 'r+b')	# consider default mode?
		self.nt_file.seek(self.boflen)	# if bof written > zero : will simply be zero
		self.tmpbio = BytesIO(self.nt_file.read())
		self.nt_file.seek(self.boflen)
		return True

	# The ordering of sequences in the PRONOM database may prevent the
	# successful generation of a skeleton file. Detect these issues and
	# provide feedback to users as a warning.
	def detect_write_issues(self, POS):
		
		error_str = string.ljust("(" + self.puid_str + "): ", 13, ' ')
		info_str = string.ljust("INFO:", 9, ' ')
		warn_str = string.ljust("WARNING:", 9, ' ')
		
		'''if POS == self.BOF:
			if self.bof_written == True:
				sys.stderr.write(warn_str + error_str + "Attempting to write BOF with BOF written." + "\n")
			if self.eof_written == True:
				sys.stderr.write(info_str + error_str + "Attempting to write BOF with EOF written." + "\n")
		elif POS == self.EOF:
			if self.eof_written == True:
				sys.stderr.write(warn_str + error_str + "Attempting to write EOF with EOF written." + "\n")
		elif POS == self.VAR:
			if self.var_written == True:
				sys.stderr.write(warn_str + error_str + "Attempting to write VAR with VAR written." + "\n")
			if self.eof_written == True:
				sys.stderr.write(info_str + error_str + "Attempting to write VAR with EOF written." + "\n")'''
