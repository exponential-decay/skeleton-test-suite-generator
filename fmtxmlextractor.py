"""fmt and x-fmt PUID handler..."""
# -*- coding: utf-8 -*-

import sys
import xml.etree.ElementTree as etree
from collections import OrderedDict

import filewriter

# Here we're going to create a structure and a list to handle the ordering
# of Signature byte sequences...


class ByteSequence:
    """Structure of a Byte sequence in PRONOM."""

    fr = ""
    pos = ""
    min_off = ""
    max_off = ""
    seq = ""


# Order this list to be passed around...
bytesequences = []

# We also need to know which formats the sequences belong to...
instancedict = {}

fmt_no = 0  # to be incremented as we create a new uri for each sfw resource
header_list = []  # To potentially store metadata for these files
content_list = []  # To store the data we're interested in
signature_id_name = []  # TMP to store sig id values before adding to content_list

# TODO: Better way than using these globals? remaining from early prototype
SEQPOS = 0
MINOFF = 1
MAXOFF = 2
BYTSEQ = 3

# Sequence list is structurally always 4 parts. Items are inserted at
# the correct positions. This may be better served as part of a data
# class.
sequence_list = ["null", "null", "null", "null"]

extension = ""
ext_added = False

# Stat globals
format_sig_count = 0
record_count = 0
files_created = 0


def get_stats():
    """Structure statistics for the caller."""
    return OrderedDict(
        [
            ("Number of PRONOM records:          ", record_count),
            ("Number of formats with Signatures: ", format_sig_count),
            ("Number of files created:           ", files_created),
        ]
    )


# Handle fmt xml objects...
def handler(puid_type, number_path_pair):
    """Handle XML objects from PRONOM."""

    global record_count, fmt_no
    record_count += 1
    fmt_no = number_path_pair[0]

    file_no = number_path_pair[0]
    file_name = number_path_pair[1]

    try:
        tree = etree.parse(file_name)
        root = tree.getroot()
        xml_iter = iter(root)

        format_elem = root.find(
            "{http://pronom.nationalarchives.gov.uk}report_format_detail"
        ).find("{http://pronom.nationalarchives.gov.uk}FileFormat")

        int_sig = format_elem.findall(
            "{http://pronom.nationalarchives.gov.uk}InternalSignature"
        )
        number_of_internal_signatures = len(int_sig)
        files_to_create = number_of_internal_signatures

        global files_created
        files_created += files_to_create

        if int_sig:
            global format_sig_count
            format_sig_count += 1

            extract(puid_type, file_no, xml_iter, "")

            handle_output(puid_type, file_no)

            del header_list[:]
            del content_list[:]

            global extension, ext_added
            extension = ""
            ext_added = False

    except IOError as err:
        _ = err
        print("{err} : {file_string}", file=sys.stderr)

    global bytesequences
    bytesequences = sort_sequences(bytesequences)
    write_signature(bytesequences)
    bytesequences = []


def handle_output(puid_type, file_no):
    """Forward data to file writer object to create skeleton suite
    files.
    """
    sigID = 0

    for x in content_list:

        if x[0] == "Internal Signature ID":
            fr = filewriter.FileWriter(puid_type)  # create file writing object
            if x[1] != sigID:
                sigID = x[1]
                if content_list[1][0] == "File Extension":
                    ext = content_list[1][1]
                else:
                    ext = "nul"

                # New internal sig, new file - create
                fr.write_file(puid_type, file_no, sigID, ext)

        if x[0] == "Byte sequence":

            bs = ByteSequence()
            bs.fr = fr
            bs.pos = x[1][0]
            min_off = x[1][1]
            max_off = x[1][2]
            bs.seq = x[1][3]

            if min_off == "null":
                min_off = 0

            if max_off == "null":
                max_off = 0

            bs.min_off = int(min_off)
            bs.max_off = int(max_off)

            bytesequences.append(bs)


def sort_sequences(bs):
    """Sort byte sequences."""

    bof = []
    eof = []
    var = []

    for b in bs:
        if b.pos == "Absolute from BOF":
            bof.append(b)
        if b.pos == "Absolute from EOF":
            eof.append(b)
        if b.pos == "Variable":
            var.append(b)

    bof = sorted(bof, key=lambda b: b.min_off)
    eof = sorted(eof, key=lambda b: b.min_off, reverse=True)
    var = sorted(var, key=lambda b: b.min_off)

    bs_new = bof + var + eof

    return bs_new


def write_signature(bs):
    """Write signature given each different component."""
    for b in bs:
        if b.pos == "Absolute from BOF":
            b.fr.write_header(b.min_off, b.seq)
        if b.pos == "Absolute from EOF":
            b.fr.write_footer(b.min_off, b.seq)
        if b.pos == "Variable":
            b.fr.write_var(b.min_off, b.max_off, b.seq)


def extract(puid_type, file_no, xml_iter, parent_node):
    """Run through XML elements when we get to a node element fwd to
    node handler.
    """
    for i in xml_iter:
        index = len(i)

        if index > 0:
            # need to recurse a parent node in xml which has multiple sub nodes
            # create an iterator to do so and create a list from the iterator
            # to access the contents of the sub nodes easier.
            temporary_parent_node = strip_text(i)
            new_iter = iter(i)
            extract(puid_type, file_no, new_iter, temporary_parent_node)

        else:
            if i.text is not None:
                if ord(i.text[0]) != 10:  # check for LF character...
                    parent_text = parent_node.replace(
                        "{http://pronom.nationalarchives.gov.uk}", ""
                    )
                    node_text = strip_text(i)
                    # handle the normalization of text here... covers all puid types
                    node_value = text_replace(i.text.encode("UTF-8"))
                    parent_subnode_pair = parent_text + " " + node_text
                    node_handler(parent_subnode_pair, node_value)


def node_handler(parent_subnode_pair, node_value):
    """Given the parent and subnode in XML does it have data we're
    interested in?.
    """

    global sequence_list

    parent_subnode_pair = parent_subnode_pair.replace("'", "")

    if parent_subnode_pair == "FileFormat FormatName":
        header_list.append(["Format name", node_value.replace("  ", " ")])
    elif parent_subnode_pair == "FileFormat FormatVersion":
        header_list.append(["Format version", node_value])
    elif parent_subnode_pair == "FileFormatIdentifier Identifier":
        if "fmt" in node_value:
            header_list.append(["puid", node_value.replace("/", "-")])
            content_list.append(["puid", node_value.replace("/", "-")])
    elif parent_subnode_pair == "InternalSignature SignatureID":
        signature_id_name.append(node_value)
        content_list.append(["Internal Signature ID", node_value])
    elif parent_subnode_pair == "InternalSignature SignatureName":
        signature_id_name[0] = str(
            signature_id_name[0] + " " + node_value.replace(" ", "")
        )
        content_list.append(["Internal Signature Name", signature_id_name[0]])
        del signature_id_name[:]
    elif parent_subnode_pair == "ByteSequence ByteSequenceID":
        content_list.append(["Byte Sequence ID", node_value])
    elif parent_subnode_pair == "ByteSequence PositionType":
        sequence_list.insert(SEQPOS, node_value)
    elif parent_subnode_pair == "ByteSequence Offset":
        sequence_list.insert(MINOFF, node_value)
    elif parent_subnode_pair == "ByteSequence MaxOffset":
        sequence_list.insert(MAXOFF, node_value)
    elif parent_subnode_pair == "ByteSequence ByteSequenceValue":
        sequence_list.insert(BYTSEQ, node_value)
        content_list.append(["Byte sequence", sequence_list])
        sequence_list = ["null", "null", "null", "null"]
    elif parent_subnode_pair == "ExternalSignature Signature":
        global extension
        extension = node_value
    elif parent_subnode_pair == "ExternalSignature SignatureType":
        if node_value == "File extension":
            global ext_added
            if ext_added is False:
                header_list.append(["File Extension", extension])
                content_list.append(["File Extension", extension])
                ext_added = True


def strip_text(text):
    """Strip <Element from tags and {http:// etc..."""
    new_text = str(text).replace("<Element", "", 1)
    substr_pos = new_text[1:].find(" ")
    return new_text[1 : substr_pos + 1].replace(
        "{http://pronom.nationalarchives.gov.uk}", ""
    )


def text_replace(node_value_text):
    """Escape dodgy characters... TODO: Reworked from prev. script -
    needed??
    """
    node_value_text = node_value_text.decode("utf8")
    node_value_text = node_value_text.replace("\n", "\\n")
    node_value_text = node_value_text.replace('"', '\\"')
    node_value_text = node_value_text.replace("\t", "\\t")
    node_value_text = node_value_text.replace("\r", "\\r")
    # might cause issues...
    node_value_text = node_value_text.replace("\\", "\\\\")
    return node_value_text
