# P17_PIP_10K_Emulation
I made a simple serial interface responder written in python which fakes response of this solar inverter to test esphome's "PipSolar PV Inverter" component. 
It's a simple dispatcher only. Response can be edited, length is checked on receive (^S and ^P) and generated for the response (^D) together with the checksum. I added "zero feed compensation" and Pylontech stuff.
I took the infos from the - probably well known - blue header spreadsheet. There are some responses where the explanation regarding length field seems to be wrong.

This P17 protocol variant on RS232 uses ^ as first symbol for any information followed by its length and then followed by the command and its parameters. Only responsees (^D) then add a 16bits checksum while commands (^P and ^S) don't.
Any information is terminated by a \<cr\> symbol.
