# drsProcessing
A collection of DRS processing and analysis software

Here I have added a set of processing scripts to be used with the DRS4 (version 5+). There are two processing scripts depending on what your workflow prefers: C++ and python

(RECOMMENDED) PYTHON:
This is the more developed processing chain. There are two scripts: "v4", which is for runs taken at fixed bias voltages, and "scans", which was written to accept a .csv
with bias voltage information to be used during bias voltage sweeps.

Usage:
python processMultiBoardBinary_v4.py -b BINARYFILE [-o OUTFILE -v BIAS -x TXTDUMPBOOL -w WAVEFORMBOOL]

-b: path to the binary file you want to process
-o: Outpath to the processed ROOT output (default: ./processed)
-v: Fixed bias voltage argument
-x: Bool, if set to true will dump the waveform and processing info to a .txt file
-w: Bool, if set to true will dump the waveform into to the ROOT file

python processMultiBoardBinary_scans.py -b BINARYFILE -c CSVPATH [-o OUTFILE -w WAVEFORMBOOL]

Same as above except for:
-c: CSV file with bias voltage information, meant for bias voltage sweeps. Configured to work for a Keithley current source


(ALTERNATIVE) C++:
This is a newer chain, but depending on your workflow you might prefer it. Compile as usual with g++ -o [EXECUTABLE_NAME] process.cc, then run with:

Usage:
./process <filename> [waveFormOutBool]

filename: path to the binary file you want to process
waveFormOutBool: Bool, if set to true will dump the waveform and processing info to a .txt file

In the script itself, there is a region to add code to do event-by-event processing.


Direct any questions to Ryan Schmitz (schmitz@ucsb.edu or ryan@cern.ch).
