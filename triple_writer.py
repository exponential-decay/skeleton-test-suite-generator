from urlparse import urlparse
import std_properties
import os
import sys
import sig2map

class TripleWriter:

	##################################################
	# __init__
	# Class constructor... initialize variables here
	##################################################
	def __init__(self, puid_type):

		self.newtriplesdir = os.getcwd() + "//mapping_output_test//" + puid_type + '-bytedat-files//'

		if os.path.exists(self.newtriplesdir) == False:
			try:
				os.makedirs(self.newtriplesdir)
			except OSError as (errno, strerror):
				sys.stderr.write("OS error({0}): {1}".format(errno, strerror) + '\n')
			
		#variables to hold details about individual triple files
		self.nt_file = 0		#to hold file pointer
		self.puid_no = 0		#to hold the puid number we're looking at
		self.nt_string = 0 	#triple file path...
		self.nt_boflen = 0	#length of the bof sequence after writing
		
	##################################################
	# Validate url
	# If string is a URL put in angle brackets / literal
	##################################################
	def __validate_url(self, value):		#__ says this is a private member function
		v2 = urlparse(value)						# parse url
		if v2.scheme == 'http':					# return scheme
			value = '<' + value + '>'
		else:
			value = '"' + value + '"'
			
		return value

	##################################################
	# Write triple
	# generic function to output all purpose triple
	##################################################
	def write_metadata(self, puid, puid_no, value):
		
		#if we receive a different puid_no from the function call and it
		#doesn't match the member variable self.puid_no we are parsing a 
		#new xml file and so need a new triple file as a result...
		if self.puid_no != puid_no:
			#type will be null as class persists so don't need to check...
			#assign values to member variables...
			self.nt_string = self.newtriplesdir + puid + "-" + str(puid_no) + '-bytedat.bin'
			self.puid_no = puid_no
			#double check file existance... should be false
			if os.path.exists(self.nt_string) == False:
				self.nt_file = open(self.nt_string, 'w')
				self.nt_file.write("DROID bytedat 1.0" + '\n')

		if type(self.nt_file) == file:				# check we've initialized member variable
			self.nt_file.write("Format: " + value + '\n')

			
	def write_header(self, pos, min, max, seq):
		
		self.nt_file.seek(0)	
		bof_sequence = sig2map.map_signature(min, seq)
		
		print seq
		
		for x in bof_sequence:
		
			print x
		
			'''try:
				#s = 'd'
				s = map(ord, x.decode('hex'))
				for y in s:
					self.nt_file.write(chr(y))
			except:
				sys.stderr.write("Signature not mapped: " + seq + '\n')'''
			
		
		self.boflen = self.nt_file.tell()
		print self.boflen
		
		
	def write_footer(self, pos, min, max, seq):
	
		#print "max: " + str(min)
		#print "min: " + str(max)

		x = 1

		#sys.stdout.write(seq)
	
		#self.nt_file.seek(0,2)				# seek to end of file
		#self.nt_file.write("eof:"+seq)

	def write_var(self, pos, min, max, seq):
	
		#print "max: " + str(min)
		#print "min: " + str(max)
	
		#self.nt_file.seek(position after bof was written)
		
		#read bof end position and find suitable
		#place to write var byte sequence to
		
		#print "var"
		#self.nt_file.write("var:"+seq)
		
		
		hello = 2
		
		#sys.stdout.write(seq)
		
		
	def write_file(self, puid, puid_no, sigID, value):
		self.nt_string = self.newtriplesdir + puid + "-" + str(puid_no) + "-signature-id-" + sigID
		self.puid_no = puid_no
		if os.path.exists(self.nt_string) == False:
			self.nt_file = open(self.nt_string, 'w')
		
		#self.nt_string = self.newtriplesdir + puid + "-" + str(puid_no) + '-bytedat.bin'
		#self.puid_no = puid_no
		#double check file existance... should be false
		#if os.path.exists(self.nt_string) == False:
		#	self.nt_file = open(self.nt_string, 'w')
		#	self.nt_file.write("DROID bytedat 1.0:" + '\n')	

