from unittest import TestCase, TestLoader, TextTestRunner

import signature2bytegenerator


class Sig2ByteGeneratorTests(TestCase):
    def setup(self):
        self.sig2map = signature2bytegenerator.Sig2ByteGenerator()

    def test_set_fillbyte(self):
        self.setup()

        # check random is set correctly > 255
        self.assertEqual("Random", self.sig2map.set_fillbyte(256))

        # check random is set correctly < 255
        self.assertEqual("Random", self.sig2map.set_fillbyte(-1))

        # check specific value
        self.assertEqual(255, self.sig2map.set_fillbyte(255))

        # check we handly text i.e. set to random
        self.assertEqual("Random", self.sig2map.set_fillbyte("xyz"))

    # check function finds syntax values: ['{', '(', '[', '?', '*']
    def test_check_syntax(self):
        self.setup()

        # signatures demonstrating elements of syntax
        self.assertTrue(self.sig2map.check_syntax("ab{1}"))
        self.assertTrue(self.sig2map.check_syntax("ab{1-2}"))
        self.assertTrue(self.sig2map.check_syntax("ab(1)"))
        self.assertTrue(self.sig2map.check_syntax("ab[10:20]"))
        self.assertTrue(self.sig2map.check_syntax("ab*cd"))
        self.assertTrue(self.sig2map.check_syntax("ab??"))

        # example without syntax value
        self.assertIsNone(self.sig2map.check_syntax("abcd"))
        self.assertIsNone(self.sig2map.check_syntax(""))

    # check function creates random and non-random bytes of correct len
    def test_create_bytes(self):
        self.setup()

        # create five null bytes
        test_list = ["00", "00", "00", "00", "00"]
        self.sig2map.set_fillbyte(0)
        self.sig2map.create_bytes(5)
        self.assertEqual(test_list, self.sig2map.component_list)

        del self.sig2map.component_list[:]
        del test_list[:]

        # test generation of a different value
        test_list = ["01", "01", "01", "01", "01"]
        self.sig2map.set_fillbyte(1)
        self.sig2map.create_bytes(5)
        self.assertEqual(test_list, self.sig2map.component_list)

        del self.sig2map.component_list[:]
        del test_list[:]

        # create 50 random bytes
        list_len = 50
        self.sig2map.set_fillbyte(-1)
        self.sig2map.create_bytes(list_len)
        self.assertEqual(list_len, len(self.sig2map.component_list))

        del self.sig2map.component_list[:]

    def test_map_signature(self):
        self.setup()

        # Test complex signature with all possible syntax
        signature = "deadbeef{3}cafebabe??cafed00d{3-10}bbadf00d[aaaa:abbb]baadf00d[!facefeed]deadfa11*0defaced(aa|bb)defeca7e(ccff|dddd|eeeeee)d15ea5ed??00bab10c????deadfeed"
        result_list = [
            "deadbeef",
            "00",
            "00",
            "00",
            "cafebabe",
            "00",
            "cafed00d",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "bbadf00d",
            "ab32",
            "baadf00d",
            "f9",
            "cd",
            "fd",
            "ec",
            "deadfa11",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "0defaced",
            "aa",
            "defeca7e",
            "cc",
            "ff",
            "d15ea5ed",
            "00",
            "00bab10c",
            "00",
            "00",
            "deadfeed",
        ]

        self.sig2map.map_signature(0, signature, 0, 0)
        self.assertEqual(result_list, self.sig2map.component_list)

        del self.sig2map.component_list[:]

        # test beginning a signature with ?? syntax
        signature = "??deadfeed"
        result_list = ["00", "deadfeed"]

        self.sig2map.map_signature(0, signature, 0, 0)
        self.assertEqual(result_list, self.sig2map.component_list)

        del self.sig2map.component_list[:]

        signature = "4244{12}0003{6}[!&01]00"
        result_list = [
            "4244",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "0003",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
            "00",
        ]
        self.sig2map.map_signature(0, signature, 0, 0)
        self.assertEqual(result_list, self.sig2map.component_list)


def main():
    suite = TestLoader().loadTestsFromTestCase(Sig2ByteGeneratorTests)
    TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    main()
