"""filewriter contains the functions required for writing skeleton files
to disk.
"""
import configparser as ConfigParser
import os
import sys
from io import BytesIO

import signature2bytegenerator


class FileWriter:
    """Functions for writing skeleton files to disk."""

    def __init__(self, puid_type):

        self.eof_written = None
        self.var_written = None
        self.bof_written = None
        self.boflen = None
        self.tmpbio = None
        self.puid_str = None
        self.nt_file = None
        self.nt_string = None
        self.sig2map = None
        self.var_pos = None
        self.puid_no = None

        config = ConfigParser.RawConfigParser()
        config.read("skeletonsuite.cfg")

        self.newtriplesdir = (
            os.getcwd()
            + "//"
            + config.get("locations", "output")
            + "//"
            + puid_type
            + "//"
        )

        if os.path.exists(self.newtriplesdir) is False:
            try:
                os.makedirs(self.newtriplesdir)
            except OSError as err:
                print(err, file=sys.stderr)

        self.bof = 1  # enum-esque vars to help check already written sequences
        self.var = 2
        self.eof = 3

        try:
            self.fillbyte = config.getint("runtime", "fillbyte")
        except ValueError as err:
            print(err, file=sys.stderr)
            self.fillbyte = 0

    @staticmethod
    def int_list_from_sequence(bytes_):
        """Convert bytes to a list."""
        return list(bytes.fromhex(bytes_))

    # Write BOF sequence to file
    def write_header(self, min_, seq):
        """Write BOF to file."""

        self.sig2map = signature2bytegenerator.Sig2ByteGenerator()

        self.detect_write_issues(self.bof)
        bof_sequence = ""
        if self.bof_written is True:

            # the sequences are aligned okay...
            if int(min_) > int(self.boflen):
                # sys.stderr.write(string.ljust(" ", 22, " ") + string.rjust(grt1, 20, " ") + '\n')
                # sys.stderr.write(string.ljust(" ", 16, " ") + string.rjust(grt2, 20, " ") + '\n')
                self.nt_file.seek(self.boflen)
                mint = int(min_) - int(self.boflen)
                bof_sequence = self.sig2map.map_signature(mint, seq, 0, self.fillbyte)

            # if second sequence is zero may be error in PRONOM
            # so write after BOF to not overwrite anything
            elif int(min_) == 0:
                # sys.stderr.write(string.ljust(" ", 22, " ") + string.rjust(eq2, 20, " ") + "\n")
                # sys.stderr.write(string.ljust(" ", 18, " ") + string.rjust(eq3, 20, " ") + "\n")
                self.nt_file.seek(self.boflen)
                bof_sequence = self.sig2map.map_signature(min_, seq, 0, self.fillbyte)

            # we might not need this... may fit under min >(=) boflen
            elif int(min_) == int(self.boflen):
                bof_sequence = self.sig2map.map_signature(min_, seq, 0, self.fillbyte)

        else:

            self.nt_file.seek(0)
            bof_sequence = self.sig2map.map_signature(min_, seq, 0, self.fillbyte)

        tmpread = False
        if self.eof_written is True:  # read eof into tmp and re-write
            tmpread = self.write_seq_with_eof()

        for sequence in bof_sequence:
            try:
                bof = self.int_list_from_sequence(sequence)
                self.nt_file.write(bytes(bof))
            except TypeError as err:
                error = f"{err} BOF Signature not mapped: {seq}"
                print(error, file=sys.stderr)

        self.boflen = self.nt_file.tell()
        self.bof_written = True

        if tmpread is True:
            self.nt_file.write(self.tmpbio.getvalue())

    # Write EOF sequence to file
    def write_footer(self, min_off, seq):
        """Write skeleton file EOF."""

        self.sig2map = (
            signature2bytegenerator.Sig2ByteGenerator()
        )  # TODO: New instance or not?
        self.detect_write_issues(self.eof)

        self.nt_file.seek(0, 2)  # seek to end of file
        eof_sequence = self.sig2map.map_signature(0, seq, min_off, self.fillbyte)

        for sequence in eof_sequence:
            try:
                eof = self.int_list_from_sequence(sequence)
                self.nt_file.write(bytes(eof))
            except (TypeError, ValueError) as err:
                print(f"EOF Signature not mapped: {seq} ({err})\n", file=sys.stderr)

        self.eof_written = True

    def write_var(self, min_, max_, seq):
        """Write variable sequences to file."""
        self.sig2map = (
            signature2bytegenerator.Sig2ByteGenerator()
        )  # TODO: New instance or not?
        self.detect_write_issues(self.var)

        if self.var_written is False:
            self.var_pos = self.boflen
            self.var_written = True

        self.nt_file.seek(self.var_pos)
        var_sequence = self.sig2map.map_signature(
            min_, seq, max_, self.fillbyte
        )  # padding sequence

        tmpread = False
        if self.eof_written is True:  # read eof into tmp and re-write
            tmpread = self.write_seq_with_eof()

        for sequence in var_sequence:
            try:
                var = self.int_list_from_sequence(sequence)
                self.nt_file.write(bytes(var))
            except (TypeError, ValueError) as err:
                _ = err
                print("VAR Signature not mapped: {seq} ({err})\n", file=sys.stderr)

        if tmpread is True:
            self.nt_file.write(self.tmpbio.getvalue())

        self.var_pos = self.nt_file.tell()
        self.var_written = True

    def write_file(self, puid, puid_no, signature_id, ext):
        """Create a new file."""
        self.nt_string = (
            f"{self.newtriplesdir}{puid}-{puid_no}-signature-id-{signature_id}.{ext}"
        )
        self.puid_no = puid_no
        if os.path.exists(self.nt_string) is False:
            # to standard out so as not to clutter error log...
            sys.stdout.write("Writing " + str(os.path.basename(self.nt_string)) + "\n")
            self.nt_file = open(self.nt_string, "wb")

        self.puid_str = puid + "/" + str(self.puid_no)

        # Vars to ensure we know what sequences have been written
        self.bof_written = False
        self.var_written = False
        self.eof_written = False
        self.boflen = 0  # init or here, no problem

        return self.puid_str

    def write_seq_with_eof(self):
        """We can attempt to write a var or BOF sequence with EOF
        already written by creating a tmp location for the EOF data
        while we write the VAR out.
        """
        self.nt_file.close()
        self.nt_file = open(self.nt_string, "r+b")  # consider default mode?
        self.nt_file.seek(self.boflen)  # if bof written > zero : will simply be zero
        self.tmpbio = BytesIO(self.nt_file.read())
        self.nt_file.seek(self.boflen)
        return True

    def detect_write_issues(self, pos):
        """The ordering of sequences in the PRONOM database may prevent
        the successful generation of a skeleton file. Detect these
        issues and provide feedback to users as a warning.
        """

        error_str = str.ljust("(" + self.puid_str + "): ", 13, " ")
        info_str = str.ljust("INFO:", 9, " ")
        warn_str = str.ljust("WARNING:", 9, " ")

        if pos == self.bof:
            if self.bof_written is True:
                print(
                    f"{warn_str}{error_str}Attempting to write BOF with BOF written.",
                    file=sys.stderr,
                )
            if self.eof_written is True:
                print(
                    f"{info_str}{error_str}Attempting to write BOF with EOF written.",
                    file=sys.stderr,
                )
        elif pos == self.eof:
            if self.eof_written is True:
                print(
                    f"{warn_str}{error_str}Attempting to write EOF with EOF written.",
                    file=sys.stderr,
                )
        elif pos == self.var:
            if self.var_written is True:
                print(
                    f"{warn_str}{error_str}Attempting to write VAR with VAR written.",
                    file=sys.stderr,
                )
            if self.eof_written is True:
                print(
                    f"{info_str}{error_str}Attempting to write VAR with EOF written.",
                    file=sys.stderr,
                )
