"""Tests for skeleton suite generator."""

import signature2bytegenerator


def test_set_fillbyte():
    """Tests that fill byte functions work as anticipated."""

    sig2map = signature2bytegenerator.Sig2ByteGenerator()

    # check random is set correctly > 255
    sig2map.set_fillbyte(256)
    assert "Random" == sig2map.fillbyte

    # check random is set correctly < 255
    sig2map.set_fillbyte(-1)
    assert "Random" == sig2map.fillbyte

    # check specific value
    sig2map.set_fillbyte(255)
    assert 255 == sig2map.fillbyte

    # check we handly text i.e. set to random
    sig2map.set_fillbyte("xyz")
    assert "Random" == sig2map.fillbyte


def test_check_syntax():
    """Check function finds syntax values: ['{', '(', '[', '?', '*']."""
    sig2map = signature2bytegenerator.Sig2ByteGenerator()

    # signatures demonstrating elements of syntax
    assert sig2map.check_syntax("ab{1}") is True
    assert sig2map.check_syntax("ab{1-2}") is True
    assert sig2map.check_syntax("ab(1)") is True
    assert sig2map.check_syntax("ab[10:20]") is True
    assert sig2map.check_syntax("ab*cd") is True
    assert sig2map.check_syntax("ab??") is True

    # example without syntax value
    assert sig2map.check_syntax("abcd") is None
    assert sig2map.check_syntax("") is None


def test_create_bytes():
    """Check function creates random and non-random bytes of correct
    length.
    """
    sig2map = signature2bytegenerator.Sig2ByteGenerator()

    # create five null bytes
    test_list = ["00", "00", "00", "00", "00"]
    sig2map.set_fillbyte(0)
    sig2map.create_bytes(5)
    assert test_list == sig2map.component_list

    del sig2map.component_list[:]
    del test_list[:]

    # test generation of a different value
    test_list = ["01", "01", "01", "01", "01"]
    sig2map.set_fillbyte(1)
    sig2map.create_bytes(5)
    assert test_list == sig2map.component_list

    del sig2map.component_list[:]
    del test_list[:]

    # create 50 random bytes
    list_len = 50
    sig2map.set_fillbyte(-1)
    sig2map.create_bytes(list_len)
    assert list_len == len(sig2map.component_list)

    del sig2map.component_list[:]


def test_map_signature():
    """Tests that signatures map as anticipated."""

    sig2map = signature2bytegenerator.Sig2ByteGenerator()

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

    sig2map.map_signature(0, signature, 0, 0)
    assert result_list == sig2map.component_list

    del sig2map.component_list[:]

    # test beginning a signature with ?? syntax
    signature = "??deadfeed"
    result_list = ["00", "deadfeed"]

    sig2map.map_signature(0, signature, 0, 0)
    assert result_list == sig2map.component_list

    del sig2map.component_list[:]

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
    sig2map.map_signature(0, signature, 0, 0)
    assert result_list == sig2map.component_list
