This repository includes scripts to convert an EAD file to MARCXML that were written specifically for the two archival collections of Solent University:
-the papers of the TV writer/producer Philip Mackie
-a mainly photographic collection from the film director Ken Russell.

The script will not be re-useable without some editing because:
- it creates some hard coded fields specific to the collection (e.g., 040, 100, 541)
- it attempts to parse the scopecontent EAD field into the 505 and 520 fields in MARC, and it depends on a particular type of formatting in the scopecontent field that was agreed internally at Solent.

The script is a pragmatic response to the challenge of converting EAD to MARC. If the data in the EAD is not formatted as expected, it will not produce a perfect record, but it would always be possible to perform a manual check after the records were created.

In each subfolder - one for each collection - I have put the original EAD, the Python script, and the resulting MARCxml.
