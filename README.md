#**Skeleton test suite generator** (skeleton-suite-generator)
---

Herein lies the scripts for the automated generation of digital 
objects based on the digital signatures documented in the PRONOM database 
maintained by The National Archives, UK. 

The skeleton-suite-generator serves to fill the gap that exists whereby 
the community requires a corpus of digital objects for the validation and
evaluation of format identification tools and techniques. The tool 
should be used to complement a methodology whereby skeleton 
files are also generated manually by signature developers. 

The tool takes a signature specified for a digital object in PRONOM and 
constructs a digital object that will match its footprint. For example, 
given the signature:

    CAFED00D{4}CAFEBABE(0D|0D0A)

The hex sequence which composes a digital object that will match 
this signature in DROID will look like the following:

    CADED00D00000000CAFEBABE0D0A

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
*500kb* in size. 

Does not suffer issues relating to IPR and copyright. The suite and 
generator tool, licensed under CC BY-SA (see below).

The tool so far is a prototype and it doesn't handle every sequence in 
PRONOM as of yet. Signatures with multiple BOF sequences, for example, 
will not generate correctly. While this can be corrected by the team 
working on PRONOM, these are legitimate sequences that should be handled 
by the tool. 

###TODO

* Handle multiples of sequence types, e.g. multiple non-colliding BOF 
sequences.

* Understand the requirements for metadata to be associated with files, 
e.g. should the internal structure of files be self-describing?

* A repository needs to be created on GitHub to host the first 
non-prototypical output of this generator and the test-suite henceforth.

* Understand what do we need to do with multiple combinations of byte 
sequences - currently we *always* turn-left.  

###License

<a rel="license" href="http://creativecommons.org/licenses/by-sa/3.0/"><img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by-sa/3.0/80x15.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/3.0/">Creative Commons Attribution-ShareAlike 3.0 Unported License</a>.
