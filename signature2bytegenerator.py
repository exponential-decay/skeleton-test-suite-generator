import random


class Sig2ByteGenerator:
    def __init__(self):
        self.component_list = []
        self.open_syntax = ["{", "(", "[", "?", "*"]
        self.fillbyte = -1

    def __del__(self):
        del self.component_list[:]

    @staticmethod
    def int_list_from_sequence(bytes_):
        """Convert bytes to a list."""
        return [byte_ for byte_ in bytes.fromhex(bytes_)]

    def set_fillbyte(self, fillvalue):
        if not (isinstance(fillvalue, int)):
            self.fillbyte = "Random"
            return
        if fillvalue < 0 or fillvalue > 255:
            self.fillbyte = "Random"
            return
        self.fillbyte = fillvalue
        return

    def check_syntax(self, signature):
        for i in self.open_syntax:
            if signature.find(i) > -1:
                return True

    def create_bytes(self, no):
        for i in range(int(no)):
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
        # convert to ints and find mean value in range
        if syn.find(":") > -1:
            new_str = syn.split(":")
            val = (int(new_str[0], 16) + int(new_str[1], 16)) / 2
            hx = hex(int(val)).replace("0x", "").zfill(2).replace("L", "")
            # this is a hack to solve issue #8 we've never come across it before
            # but it could conceivably happen again... depends how large the value
            # is following a colon and if the hex representation is odd numbered
            if len(hx) % 2 != 0:
                hx = hex(val).replace("0x", "").zfill(len(hx) + 1).replace("L", "")
            self.component_list.append(hx)

    def sqr_not(self, syn):
        syn = syn.replace("!", "")
        s = self.int_list_from_sequence(syn)
        i = 0
        print(str(s))
        for h in s:  # this function could be seriously busted - check
            if s[i] == 0:
                s[i] = s[i] + 1
            else:
                s[i] = s[i] - 1
            self.component_list.append(
                hex(s[i]).replace("0x", "").zfill(2).replace("L", "")
            )
            i += 1

    def process_thesis(self, syn):
        syn = syn.replace("(", "").replace(")", "")

        index = syn.find("|")
        syn = syn[0:index]

        if syn.find("[") == -1:
            s = self.int_list_from_sequence(syn)
            for i in range(s.__len__()):
                self.component_list.append(
                    hex(s[i]).replace("0x", "").zfill(2).replace("L", "")
                )
        else:
            self.process_square(syn)

    def detailed_check(self, signature):

        index = 0

        if signature.__len__() > 0:
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
                else:
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
        if signature != "":
            if self.check_syntax(signature) is True:
                i = 0
                for x in signature:
                    if not x.isalnum():  # are all alphanumeric
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

        self.set_fillbyte(fillvalue)

        if bofoffset != "null":
            self.create_bytes(int(bofoffset))  # dangerous? need to check type?

        self.process_signature(signature)

        if eofoffset != "null":
            self.create_bytes(int(eofoffset))

        return self.component_list
