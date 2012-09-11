# TODO: Create a class out of these functions, especially for use of
# constructor, destructor to handle the cleardown of globals, specifically
# the component_list as this needs clearing manually at beginning of script.

import binascii
import random

component_list = []

open_syntax = ['{', '(', '[', '?', '*']

def check_syntax(signature, syntax_list):
	for i in syntax_list:
		if signature.find(i) > -1: 
			return True

def create_bytes(no):
	for i in range(no):
		component_list.append(hex(random.randint(18, 255)).replace('0x', ''))
	return True

def process_curly(syn):
	
	syn = syn.replace('{', '')
	syn = syn.replace('}', '')
	
	if syn.find('-') == -1:
		create_bytes(int(syn))
	else:
		new_str = syn.split('-')
		if new_str[1] == '*':
			val = int(new_str[0])
			create_bytes(val + 10)
		else: 
			val = (int(new_str[0]) + int(new_str[1])) / 2			
			create_bytes(val)

def process_square(syn):

	syn = syn.replace('[', '')
	syn = syn.replace(']', '')
	
	#convert to ints and find mean value in range
	if syn.find(':') > -1:
		sqr_colon(syn)
	
	#convert to ints and -1 so don't equal hex in not clause
	elif syn.find('!') > -1:
		sqr_not(syn)

def sqr_colon(syn):
	#convert to ints and find mean value in range
	if syn.find(':') > -1:
		new_str = syn.split(':')
		val = (int(new_str[0], 16) + int(new_str[1], 16)) / 2
		component_list.append(hex(val).replace('0x', ''))
		
def sqr_not(syn):
	syn = syn.replace('!', '')
	s = map(ord, syn.decode('hex'))
	i = 0
	for h in s:
		s[i] = s[i]-1
		component_list.append(hex(s[i]).replace('0x', ''))
		i+=1
	
def process_thesis(syn):
	syn = syn.replace('(','').replace(')','')
	
	index = syn.find('|')
	syn = syn[0:index]
	
	if syn.find('[') == -1:
		s = map(ord, syn.decode('hex'))
		for i in range(s.__len__()):
			component_list.append(hex(s[i]).replace('0x', ''))
	else:
		print "need to handle this: " + syn
		
	return True

def detailed_check(signature):

	index = 0

	if signature.__len__() > 0:

		check_byte = signature[0]
		if check_byte == '{':
			index = signature.find('}')
			syn = signature[0:index+1]
			process_curly(syn)
		elif check_byte == '[':
			index = signature.find(']')
			syn = signature[0:index+1]
			process_square(syn)
		elif check_byte == '?':
			syn = signature[0:index]
			index = 1
			create_bytes(1)
		elif check_byte == '(':
			index = signature.find(')')
			syn = signature[0:index+1]
			#process_thesis(syn)
		elif check_byte == '*':
			create_bytes(20)
	
	return signature[index+1:]
	
def process_signature(signature):

	if check_syntax(signature, open_syntax) == True:
		i = 0
		for x in signature:		
			if not x.isalnum():		# are all alphanumeric
				component_list.append(signature[0:i])
				signature = detailed_check(signature[i:])
				break
			i+=1
		process_signature(signature)
	else:
		component_list.append(signature)

def map_signature(signature):

	if component_list:
		global component_list
		component_list = []

	process_signature(signature)
	
	return component_list