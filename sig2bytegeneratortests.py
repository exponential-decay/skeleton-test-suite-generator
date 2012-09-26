from unittest import TestCase, TestLoader, TextTestRunner
import signature2bytegenerator as sig2map

class Sig2ByteGeneratorTests(TestCase):

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
		
def main():
	suite = TestLoader().loadTestsFromTestCase(Sig2ByteGeneratorTests)
	TextTestRunner(verbosity=2).run(suite)
	
if __name__ == "__main__":
	main()