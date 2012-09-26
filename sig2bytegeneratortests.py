from unittest import main, TestCase
import signature2bytegenerator as sig2map

class Sig2ByteGeneratorTests(TestCase):

	#def setUp(self):
	#	self.txt = 'txt'

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
		
if __name__ == "__main__":
    main()