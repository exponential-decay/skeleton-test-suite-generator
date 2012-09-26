from unittest import TestCase, TestLoader, TextTestRunner
import signature2bytegenerator as sig2map

class Sig2ByteGeneratorTests(TestCase):

	def test_set_fillbyte(self):
	
		# check random is set correctly > 255
		self.assertEqual('Random', sig2map.set_fillbyte(256))
		
		# check random is set correctly < 255
		self.assertEqual('Random', sig2map.set_fillbyte(-1))		
	
		# check specific value
		self.assertEqual(255, sig2map.set_fillbyte(255))
		
		# check we handly text i.e. set to random
		self.assertEqual('Random', sig2map.set_fillbyte("xyz"))
	
	# check function finds syntax values: ['{', '(', '[', '?', '*']
	def test_check_syntax(self):
	
		# signatures demonstrating elements of syntax
		self.assertTrue(sig2map.check_syntax("ab{1}"))
		self.assertTrue(sig2map.check_syntax("ab{1-2}"))
		self.assertTrue(sig2map.check_syntax("ab(1)"))
		self.assertTrue(sig2map.check_syntax("ab[10:20]"))
		self.assertTrue(sig2map.check_syntax("ab*cd"))
		self.assertTrue(sig2map.check_syntax("ab??"))		
		
		# example without syntax value
		self.assertIsNone(sig2map.check_syntax("abcd"))
		self.assertIsNone(sig2map.check_syntax(""))
		
	# check function creates random and non-random bytes of correct len
	def test_create_bytes(self):
	
		# create five null bytes
		test_list = ['00', '00', '00', '00', '00']
		sig2map.set_fillbyte(0)
		sig2map.create_bytes(5)
		self.assertEqual(test_list, sig2map.component_list)
		
		del sig2map.component_list[:]
		del test_list[:]
		
		# test generation of a different value
		test_list = ['01', '01', '01', '01', '01']
		sig2map.set_fillbyte(1)
		sig2map.create_bytes(5)
		self.assertEqual(test_list, sig2map.component_list)
		
		del sig2map.component_list[:]
		del test_list[:]
		
		# create 50 random bytes
		list_len = 50
		sig2map.set_fillbyte(-1)
		sig2map.create_bytes(list_len)
		self.assertEqual(list_len, len(sig2map.component_list))
		
		del sig2map.component_list[:]
		
	def test_map_signature(self):
		
		# Test complex signature with all possible syntax					
		signature = "deadbeef{3}cafebabe??cafed00d{3-10}bbadf00d[aaaa:abbb]baadf00d[!facefeed]deadfa11*0DEFACED(AA|BB)DEFECA7E(CCFF|DDDD|EEEEEE)D15EA5ED??00BAB10C????DEADFEED"
		result_list = ['deadbeef','00','00','00','cafebabe','00','cafed00d'
					,'00','00','00','00','00','00','bbadf00d','ab32','baadf00d'
					,'f9', 'cd', 'fd', 'ec','deadfa11','00','00','00','00','00','00','00','00','00','00'
					,'00','00','00','00','00','00','00','00','00','00','0DEFACED','aa','DEFECA7E','cc','ff'
					,'D15EA5ED','00','00BAB10C','00','00','DEADFEED']
		
		sig2map.map_signature(0, signature, 0, 0)
		self.assertEqual(result_list, sig2map.component_list)
		
		del sig2map.component_list[:]
		
		#test beginning a signature with ?? syntax
		signature = "??deadfeed"
		result_list = ['00','deadfeed']
		
		sig2map.map_signature(0, signature, 0, 0)
		self.assertEqual(result_list, sig2map.component_list)
		
		del sig2map.component_list[:]
		
def main():
	suite = TestLoader().loadTestsFromTestCase(Sig2ByteGeneratorTests)
	TextTestRunner(verbosity=2).run(suite)
	
if __name__ == "__main__":
	main()