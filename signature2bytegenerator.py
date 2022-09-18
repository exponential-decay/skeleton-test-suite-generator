"""Converts a PRONOM signature sequence to byte sequences."""
import random


class Sig2ByteGenerator:
    """Converts PRONOM syntax to bytes for writing to file."""

    def __init__(self):
        self.component_list = []
        self.open_syntax = ["{", "(", "[", "?", "*"]
        self.fillbyte = -1

    def __del__(self):
        del self.component_list[:]

    @staticmethod
    def int_list_from_sequence(bytes_):
        """Convert bytes to a list."""
        return list(bytes.fromhex(bytes_))

    def set_fillbyte(self, fillvalue):
        """Set the fill-byte for the class instance."""
        if not isinstance(fillvalue, int):
            self.fillbyte = "Random"
            return
        if fillvalue < 0 or fillvalue > 255:
            self.fillbyte = "Random"
            return
        self.fillbyte = fillvalue
        return

    def check_syntax(self, signature):
        """If a signature component appears more than once in a
        signature it should error.
        """
        for i in self.open_syntax:
            if signature.find(i) > -1:
                return True
        return False

    def create_bytes(self, number):
        """Create bytes for a signature sequence."""
        for _ in range(int(number)):
            if self.fillbyte == "Random":
                self.component_list.append(
                    hex(random.randint(0, 255))
                    .replace("0x", "")
                    .zfill(2)
                    .replace("L", "")
                )
            else:
                self.component_list.append(
                    hex(self.fillbyte).replace("0x", "").zfill(2).replace("L", "")
                )
        return True

    def process_curly(self, syn):
        """Process curly bracket syntax from PRONOM."""
        syn = syn.replace("{", "")
        syn = syn.replace("}", "")

        if syn.find("-") == -1:
            self.create_bytes(int(syn))
        else:
            new_str = syn.split("-")
            if new_str[1] == "*":
                val = int(new_str[0])
                self.create_bytes(val + 10)
            else:
                val = (int(new_str[0]) + int(new_str[1])) / 2
                self.create_bytes(val)

    def process_square(self, syn):
        """Process square bracket syntax from PRONOM."""
        syn = syn.replace("[", "")
        syn = syn.replace("]", "")

        # convert to ints and find mean value in range
        if syn.find(":") > -1:
            self.sqr_colon(syn)

        # convert to ints and -1 so don't equal hex in not clause
        elif syn.find("!") > -1:
            self.sqr_not(syn)

    # TODO: Copy and paste from container work... make submodule
    def process_mask(self, syn, inverted=False):
        """Process mask syntax from PRONOM."""
        syn = syn.replace("[", "")
        syn = syn.replace("]", "")

        val = 0

        # negate first, else, mask...
        if "!&" in syn and inverted is True:
            syn = syn.replace("!&", "")
            byte = int(syn, 16)
            mask = byte & 0
            val = mask
        elif "&" in syn and inverted is False:
            syn = syn.replace("&", "")
            byte = int(syn, 16)
            mask = byte & 255
            val = mask

        self.component_list.append(hex(val).replace("0x", "").zfill(2).replace("L", ""))

    def sqr_colon(self, syn):
        """Process colon syntax in square bracket syntax from PRONOM."""

        # convert to ints and find mean value in range
        if syn.find(":") > -1:
            new_str = syn.split(":")
            val = (int(new_str[0], 16) + int(new_str[1], 16)) / 2
            hex_ = hex(int(val)).replace("0x", "").zfill(2).replace("L", "")
            # this is a hack to solve issue #8 we've never come across it before
            # but it could conceivably happen again... depends how large the value
            # is following a colon and if the hex representation is odd numbered
            if len(hex_) % 2 != 0:
                hex_ = (
                    hex(int(val))
                    .replace("0x", "")
                    .zfill(len(hex_) + 1)
                    .replace("L", "")
                )
            self.component_list.append(hex_)

    def sqr_not(self, syn):
        """Process negated square bracket syntax from PRONOM."""

        syn = syn.replace("!", "")
        sequence = self.int_list_from_sequence(syn)
        idx = 0
        for _ in sequence:  # this function could be seriously busted - check
            if sequence[idx] == 0:
                sequence[idx] = sequence[idx] + 1
            else:
                sequence[idx] = sequence[idx] - 1
            self.component_list.append(
                hex(sequence[idx]).replace("0x", "").zfill(2).replace("L", "")
            )
            idx += 1

    def process_thesis(self, syn):
        """Process parenthesis syntax from PRONOM."""
        syn = syn.replace("(", "").replace(")", "")
        index = syn.find("|")
        syn = syn[0:index]
        if syn.find("[") == -1:
            sequence = self.int_list_from_sequence(syn)
            for item in sequence:
                self.component_list.append(
                    hex(item).replace("0x", "").zfill(2).replace("L", "")
                )
        else:
            self.process_square(syn)

    def detailed_check(self, signature):
        """Perform a more detailed check of PRONOM syntax."""
        index = 0
        if len(signature) > 0:
            check_byte = signature[0]
            if check_byte == "{":
                index = signature.find("}")
                syn = signature[0 : index + 1]
                self.process_curly(syn)
            elif check_byte == "[":
                # if we have a bytemask.
                check_inverted = signature[1:3]
                if check_inverted == "!&":
                    index = signature.find("]")
                    syn = signature[1 : index + 1]
                    self.process_mask(syn, True)
                    return signature[index + 1 :]

                check_mask = signature[1:2]
                if check_mask == "&":
                    index = signature.find("]")
                    syn = signature[0 : index + 1]
                    self.process_mask(syn)
                    return signature[index + 1 :]

                # bytemask work ends.
                index = signature.find("]")
                syn = signature[0 : index + 1]
                self.process_square(syn)
            elif check_byte == "?":
                syn = signature[0:index]
                index = 1
                self.create_bytes(1)
            elif check_byte == "(":
                index = signature.find(")")
                syn = signature[0 : index + 1]
                self.process_thesis(syn)
            elif check_byte == "*":
                self.create_bytes(20)
        return signature[index + 1 :]

    def process_signature(self, signature):
        """Process a signature provided by the caller."""
        if signature != "":
            if self.check_syntax(signature) is True:
                i = 0
                for item in signature:
                    if not item.isalnum():  # are all alphanumeric
                        element = signature[0:i]
                        if element != "":  # may not be anything to append e.g. '??ab'
                            self.component_list.append(element)
                        signature = self.detailed_check(signature[i:])
                        break
                    i += 1
                self.process_signature(signature)
            else:
                self.component_list.append(signature)

    def map_signature(self, bofoffset, signature, eofoffset, fillvalue=-1):
        """Map a signature from PRONON."""
        self.set_fillbyte(fillvalue)
        if bofoffset != "null":
            self.create_bytes(int(bofoffset))  # dangerous? need to check type?
        self.process_signature(signature)
        if eofoffset != "null":
            self.create_bytes(int(eofoffset))
        return self.component_list
