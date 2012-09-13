# fmt and x-fmt PUID handler...
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as etree
import std_properties as std
import triple_writer
import sys
import re

tr = 0						# to store instance of triple w(r)iter object
subject_uri = ''			# to hold uri for subject written in triples
fmt_no = 0					# to be incremented as we create a new uri for each sfw resource
x_to_puid_init = 500 	# initial value to assign puids to x-puids and increment from
sig_uri = ''				# variable to hold internal signature uri
byte_uri = ''				# variable to hold byte sequence uri

header_list = []			# globals - can be removed if so inclined, for ease of dev
content_list = []			# globals - can be removed if so inclined, for ease of dev
signature_id_name = []	# globals - can be removed if so inclined, for ease of dev 
sequence_list = ['null','null','null','null']

SEQPOS = 0
MINOFF = 1
MAXOFF = 2
BYTSEQ = 3

extension = ''
ext_added = False

def reset_sequence_list():
	global sequence_list
	del sequence_list
	sequence_list = ['null','null','null','null']

##################################################
# 
# 
##################################################
def handler(puid_type, number_path_pair):

	global fmt_no
	fmt_no = number_path_pair[0]
	
	global subject_uri
	subject_uri = '<http://reference.data.gov.uk/id/file-format/' + str(fmt_no) + '>'

	#create triple writing object to handle majority of output functions
	global tr
	tr = triple_writer.TripleWriter(puid_type)
	
	file_no = number_path_pair[0]
	file_name = number_path_pair[1]
	
	try:
		tree = etree.parse(file_name)
		root = tree.getroot()
		xml_iter = iter(root)

		format_elem = root.find('{http://pronom.nationalarchives.gov.uk}report_format_detail').find('{http://pronom.nationalarchives.gov.uk}FileFormat')
		
		int_sig = format_elem.findall('{http://pronom.nationalarchives.gov.uk}InternalSignature')
		number_of_internal_signatures = len(int_sig)
		files_to_create = number_of_internal_signatures

		if int_sig:
			
			puid_str = puid_type + '/' + str(file_no)
			
			
			#tr.write_metadata(puid_type, file_no, puid_str)
			
			
			extract(puid_type, file_no, xml_iter, '')
			
			
			handle_output(puid_type, puid_str, file_no, number_of_internal_signatures)



			del header_list[:]
			del content_list[:]
			
			global extension
			extension = ''
			global ext_added
			ext_added = False


	except IOError as (errno, strerror):
		sys.stderr.write("IO error({0}): {1}".format(errno, strerror) + ' : ' + file_string + '\n')

def handle_output(puid_type, puid_str, file_no, int_sig_no):

	count = 0
	sigID = 0

	for x in content_list:
	
		if x[0] == 'Internal Signature ID':
			if x[1] != sigID:
				sigID = x[1]
				
				if content_list[1][0] == 'File Extension':
					ext = content_list[1][1]
				else:
					ext = 'nul'
				
				#create a new file
				tr.write_file(puid_type, file_no, sigID, puid_str, ext)

		if x[0] == 'Byte sequence':
			if x[1][0] == 'Absolute from BOF':
				tr.write_header(x[1][0],x[1][1],x[1][2],x[1][3])
			if x[1][0] == 'Absolute from EOF':
				tr.write_footer(x[1][0],x[1][1],x[1][2],x[1][3])
			if x[1][0] == 'Variable':
				tr.write_var(x[1][0],x[1][1],x[1][2],x[1][3])

##################################################
# 
# 
##################################################
def extract(puid_type, file_no, xml_iter, parent_node):

	for i in xml_iter:
		index = len(i)	
		
		if index > 0:
			#need to recurse a parent node in xml which has multiple sub nodes
			#create an iterator to do so and create a list from the iterator
			#to access the contents of the sub nodes easier. 
			temporary_parent_node = std.strip_text(i)
			new_iter = iter(i)

			#exceptions can go here, e.g. if exception equals true then go into 
			#exception handler, else extract(...)
			xml_exception_handled = False
			xml_exception_handled = node_exception_handler(puid_type, file_no, temporary_parent_node, new_iter)

			if xml_exception_handled == False:
				extract(puid_type, file_no, new_iter, temporary_parent_node)
				
		else:

			if i.text != None:
			
				if ord(i.text[0]) != 10:		#check for LF character...
				
					parent_text = parent_node.replace('{http://pronom.nationalarchives.gov.uk}', '')

					node_text = std.strip_text(i)
					node_text = node_text.replace('{http://pronom.nationalarchives.gov.uk}', '')
					
					#handle the normalization of text here... covers all puid types
					node_value = std.text_replace(i.text.encode('UTF-8'))
					
					parent_subnode_pair = parent_text + ' ' + node_text
					compare_result = False

					node_handler(puid_type, file_no, parent_subnode_pair, node_value)

def node_handler(puid_type, puid_no, parent_subnode_pair, node_value):
	
	parent_subnode_pair = parent_subnode_pair.replace("'", "")
	
	if parent_subnode_pair == 'FileFormat FormatName':
		#content_list.append(["Format name", node_value.replace(" ", " ")])
		header_list.append(["Format name", node_value.replace("  ", " ")])
	elif parent_subnode_pair == 'FileFormat FormatVersion':
		#content_list.append(["Format version", node_value.replace(" ", " ")])
		header_list.append(["Format version", node_value])
		
	elif parent_subnode_pair == 'FileFormatIdentifier Identifier':
		if 'fmt' in node_value:
			header_list.append(["puid", node_value.replace("/", "-")]) 
			content_list.append(["puid", node_value.replace("/", "-")]) 
		
	elif parent_subnode_pair == 'InternalSignature SignatureID':
	
		signature_id_name.append(node_value)
		content_list.append(["Internal Signature ID", node_value])
	
	elif parent_subnode_pair == 'InternalSignature SignatureName':
		
		#print node_value
		
		#print node_value.replace(' ', '')
		
		#create a file number based on integers in path
		#attempt to create a file name... add the version no to it?
		#hmm, but what if signature is versioned by text??
		#content list describes the file. 
		
		#file_no = re.findall('[0-9]', node_value)
		#print file_no
		
		signature_id_name[0] = str(signature_id_name[0] + " " + node_value.replace(' ', ''))
		
		content_list.append(["Internal Signature Name", signature_id_name[0]])
		
		del signature_id_name[:]
		
	elif parent_subnode_pair == 'ByteSequence ByteSequenceID':
		content_list.append(["Byte Sequence ID", node_value])
	elif parent_subnode_pair == 'ByteSequence PositionType':
		sequence_list.insert(SEQPOS, node_value)
	elif parent_subnode_pair == 'ByteSequence Offset':
		sequence_list.insert(MINOFF, node_value)
	elif parent_subnode_pair == 'ByteSequence MaxOffset':
		sequence_list.insert(MAXOFF, node_value)
	elif parent_subnode_pair == 'ByteSequence ByteSequenceValue':
		sequence_list.insert(BYTSEQ, node_value)
		content_list.append(["Byte sequence", sequence_list])
		reset_sequence_list()
		
	elif parent_subnode_pair == 'ExternalSignature Signature':
		global extension
		extension = node_value
	elif parent_subnode_pair == 'ExternalSignature SignatureType':	
		if node_value == 'File extension':	
			global ext_added
			if ext_added == False:
				header_list.append(["File Extension", extension])
				content_list.append(["File Extension", extension])
				ext_added = True

##################################################
# 
# 
##################################################
def file_creator(puid_type, puid_no, parent_subnode_pair, node_value):

	parent_subnode_pair = parent_subnode_pair.replace("'", "")

	if parent_subnode_pair == 'FileFormat FormatName':
		tr.triple_out(puid_type, puid_no, "Format Name", std.create_literal(node_value).replace("  ", " "))
	elif parent_subnode_pair == 'FileFormat FormatVersion':
		tr.triple_out(puid_type, puid_no, "Format version", std.create_literal(node_value))
	elif parent_subnode_pair == 'InternalSignature SignatureID':
		tr.triple_out(puid_type, puid_no, "Internal Signature ID", std.create_literal(node_value))
	elif parent_subnode_pair == 'InternalSignature SignatureName':
		tr.triple_out(puid_type, puid_no, "Internal Signature Name", std.create_literal(node_value))
	elif parent_subnode_pair == 'ByteSequence ByteSequenceID':
		tr.triple_out(puid_type, puid_no, "Byte Sequence ID", std.create_literal(node_value))
	elif parent_subnode_pair == 'ByteSequence PositionType':
		tr.triple_out(puid_type, puid_no, "Sequence position", std.create_literal(node_value))
	elif parent_subnode_pair == 'ByteSequence Offset':
		tr.triple_out(puid_type, puid_no, "Min offset", std.create_literal(node_value))
	elif parent_subnode_pair == 'ByteSequence MaxOffset':
		tr.triple_out(puid_type, puid_no, "Max offset", std.create_literal(node_value))
	elif parent_subnode_pair == 'ByteSequence ByteSequenceValue':
		tr.triple_out(puid_type, puid_no, "Byte string", std.create_literal(node_value))


##################################################
# 
# 
##################################################
def node_exception_handler(puid_type, puid_no, temporary_parent_node, new_iter):

	#initialize return value here...
	rv = False

	#handling for format identifiers such as MIMETYPE, PUID etc.
	#each section of tree has identifier type followed by identifier value...
	if temporary_parent_node.replace('{http://pronom.nationalarchives.gov.uk}', '') == 'FileFormatIdentifier':
		format_identifier_node_list = list(new_iter)
		if len(format_identifier_node_list) == 2:
			rv = handle_format_identifier(puid_type, puid_no, format_identifier_node_list[1].text, format_identifier_node_list[0].text)
	elif temporary_parent_node.replace('{http://pronom.nationalarchives.gov.uk}', '') == 'ExternalSignature':
		external_sig_node_list = list(new_iter)
		if len(external_sig_node_list) == 3:
			rv = handle_external_signatures(puid_type, puid_no, external_sig_node_list[1].text, external_sig_node_list[2].text)
	elif temporary_parent_node.replace('{http://pronom.nationalarchives.gov.uk}', '') == 'RelatedFormat':
			related_format_node_list = list(new_iter)
			if len(related_format_node_list) == 4:
				rv = False
				#print str(puid_no) + ' related format work here...'
				#output to file, concatenate with global var storing primary key and uri
				#relatedformats_file.write(relatedformats_text + ' , relationship , ' + related_format_node_list[0].text + ' , id , ' + related_format_node_list[1].text + '\n')
			

	return rv