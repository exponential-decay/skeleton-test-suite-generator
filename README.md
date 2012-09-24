#DROID Skeleton Test Suite Generator *(skeleton-test-suite-generator)*
---

Herein lies a tool for the automated generation of digital 
objects based on the digital signatures documented in the PRONOM database 
maintained by The National Archives, UK. 

The skeleton-test-suite-generator serves to fill the gap that exists whereby 
the community requires a corpus of digital objects for the validation and
evaluation of format identification tools and techniques. The tool 
should be used to complement a methodology whereby skeleton 
files are also generated manually by signature developers. 

The tool takes a signature specified for a digital object in PRONOM and 
constructs a digital object that will match its footprint. For example, 
given the signature:

    CAFED00D{4}CAFEBABE(0D|0D0A)

The hex sequences comprising digital objects that will match 
this signature in DROID will look like the following:

    CA FE D0 0D 00 00 00 00 CA FE BA BE 0D

Or:

    CA FE D0 0D 00 00 00 00 CA FE BA BE 0D 0A

The scripts take an export of the PRONOM database in XML, extract the 
internal signature information belonging to each format record and 
generate the digital objects creating the 'skeleton test suite'. 

The objects can be used for:

* Understanding where signatures in the PRONOM database will conflict, 
therefore generating multiple identifications for some files. 

* Creating signatures purely based on format specifications where 
getting sample files or making them available to those able to create
signatures is extremely difficult.

* Incorporation into the DROID unit test-suite to ensure modifications 
to identification engine do not impact identification capability. 

* Test the stability of signature files over time.

Other benefits include a small footprint - zipped the suite is just over 
*160kb* in size. 

Does not suffer issues relating to IPR and copyright. The suite and 
generator tool, licensed under CC BY-SA (see below).

The tool so far is a prototype and it doesn't handle every sequence in 
PRONOM as of yet. Signatures with multiple BOF sequences, for example, 
will not generate correctly. While this can be corrected by the team 
working on PRONOM, these are legitimate sequences that should be handled 
by the tool. 

###HOWTO

    python skeletongenerator.py
    
Easy as. The scripts require the existence of the 'pronom-export' folder 
generated by the scripts in the pronom-xml-export repository: https://github.com/exponential-decay/pronom-xml-export

The input and output locations can be configured by modifying the accompanying
cfg file **skeletonsuite.cfg**.

Files are generated by default by using NULL bytes to 'fill' the file as
dictated by a signature. This can be configured in the cfg file using the
character value for the requested fill values or <0 || >255 for random bytes.

**Version information** can be displayed by running:

    python skeletongenerator.py --version

###TODO

* Handle multiples of sequence types, e.g. multiple non-colliding BOF 
sequences.

* Understand the requirements for metadata to be associated with files, 
e.g. should the internal structure of files be self-describing?

* A repository needs to be created on GitHub to host the first 
non-prototypical output of this generator and the test-suite henceforth.

* Understand what do we need to do with multiple combinations of byte 
sequences - currently we always *turn-left*.  

* Unit tests for signature2bytegenerator.py and filewriter.py as a priority.

###For the community TODO

* Incorporate suite into unit tests for DROID and FIDO

* Together understand if we can adapt this approach for the UNIX File utility

* Talk about this tool and potential approach and help to understand how to refine it!

* Sit tight as we build an infrastructure to host the *suite* itself online. 

###License

<a rel="license" href="http://creativecommons.org/licenses/by-sa/3.0/"><img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by-sa/3.0/80x15.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/3.0/">Creative Commons Attribution-ShareAlike 3.0 Unported License</a>.
