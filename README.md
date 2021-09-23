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
./process filename [waveFormOutBool]

filename: path to the binary file you want to process

waveFormOutBool: Bool, if set to true will dump the waveform and processing info to a .txt file


In the script itself, there is a region to add code to do event-by-event processing.

=====================================================

ANALYSIS:

I have included a sample ROOT processing script for event displays (Events.C) to be used with the python ROOT outputs. I also have a sample gain curve script,
makeGainCurves.py, to be used to make gain curves when running a bias voltage scan. These are samples and may not do anything useful for you, but give something 
to start from if you want to write your own script for making event displays or gain curves.

One quick way to see event displays is to plot them directly from the ROOT file (by running the python processing script and turning on WAVEFORMBOOL).
The waveforms are stored in e.g. times_2881_1 and voltages_2881_1 (where here I am using DRS4 board number 2881 and looking at channel 1) and similar for other boards/channels.
You can plot the waveform for e.g. Event 102 with: Events->Draw("voltages_2881_1:times_2881_1","Entry$==102","l")

Direct any questions to Ryan Schmitz (schmitz@ucsb.edu or ryan@cern.ch).
