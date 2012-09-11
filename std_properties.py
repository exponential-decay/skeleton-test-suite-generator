from datetime import datetime

#standard triple data we need to output for each PUID type we convert...
formatClassTriple = '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://reference.data.gov.uk/technical-registry/file-format> .'
softwareClassTriple = '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://reference.data.gov.uk/technical-registry/software-package> .'
compressionClassTriple = '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://reference.data.gov.uk/technical-registry/compression-type> .'
encodingClassTriple = '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://reference.data.gov.uk/technical-registry/character-encoding> .'

#each puid type is also a rdfs class? - a file can be of file-format type...
rdfClassTriple = '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2000/01/rdf-schema#Class> .'

#common predicates...
rdfs_label = '<http://www.w3.org/2000/01/rdf-schema#label>'
dc_description = '<http://purl.org/dc/elements/1.1/description>'
pronom_puid = '<http://reference.data.gov.uk/technical-registry/PUID>'
pronom_version = '<http://reference.data.gov.uk/technical-registry/version>'
skos_alt = '<http://www.w3.org/2004/02/skos/core#altLabel>'
skos_note = '<http://www.w3.org/2004/02/skos/core#note>'

desc1 = 'This is an outline record only, and requires further details, research or authentication to provide information that will\
 enable users to further understand the ' 
 
#desc1 + handler variable + desc2
 
desc2 = ' and to assess digital preservation risks associated with it if appropriate.'

#list of puid type to work across in script...
puids = [
		'fmt',
		'x-fmt'
	]

#date map to for date handling function
date = [
		'Jan',
		'Feb',
		'Mar',
		'Apr',
		'May',
		'Jun',
		'Jul',
		'Aug',
		'Sep',
		'Oct',
		'Nov',
		'Dec'
	]

##################################################
#	Name: 
#	Purpose: 
##################################################
def strip_text(text):

	#bug with strip for Endianess tag? - don't strip first space
	#continue as if index begins at one from this point...
	new_text = str(text).strip('<Element')
	substr_pos = new_text[1:].find(' ');
	
	#if we output new_text alone we output just the node names for all nodes that are not null... (probably some better place
	#for this comment if we try!)
	return new_text[1:substr_pos+1]


##################################################
#	Name: 
#	Purpose: 
##################################################
def text_replace(node_value_text):

	#
	# NEED TO REPLACE ALL OF THESE IN ONE GO, \\ cancelling out previous escapes...
	# TODO: better function for this...
	# import re? re.escape(txt)
	#
	#escape invalid characters...
	node_value_text = node_value_text.replace('\n','\\n')
	node_value_text = node_value_text.replace('"', '\\"')
	node_value_text = node_value_text.replace('\t', '\\t')
	node_value_text = node_value_text.replace('\r', '\\r')

	#might cause issues...
	node_value_text = node_value_text.replace('\\', '\\\\')

	return node_value_text

##################################################
#	Name: 
#	Purpose: 
##################################################
def create_literal(node_value):
	return '"' + node_value + '"'

##################################################
#	Name: 
#	Purpose: 
##################################################	
def date_handler(value):
	#example format: <http://purl.org/dc/elements/1.1/modified> "1979-01-01"^^<http://www.w3.org/2001/XMLSchemadate>.
	
	correct_format = ''
	new_val = value.split(' ', 3)
	
	if new_val[1] in date:
		format_date = new_val[2] + '-' + str(format((date.index(new_val[1])+1), "02d")) + '-' + new_val[0]
		correct_format = '"' + format_date + '"^^<http://www.w3.org/2001/XMLSchemadate>'
	else:
		print 'unable to handle date'
	
	return correct_format
