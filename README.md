# Parameter list

Area: The area (in pVs) under the pulse with the largest vMax in the event. An offset (defined below) is subtracted from the waveform to set a proper level at zero. Then, area is calculated between the endpoints using np.trapz between tStart and tEnd of the pulse (also defined below).

Width: tEnd - tStart, the width of the waveform

Offset: The average of the first 75% of bins before the waveform began, the overall shift of the waveform

Noise: Calculated as 95th percentile - 5th percentile of the vMax values between the start of the event and 75% of the way to tStart. The threshold below which is noise and above which is a pulse

tMax: The time of the vMax in the event

vMax: The largest absolute value voltage in the event. The processing will work whether this is positive or negative

vMaxEarly: The most positive voltage in the first 300 bins

vMinEarly: The most negative voltage in the first 300 bins

vFix10,20,30: The voltage recorded 20,40,60 bins after the tMax (can configure the choice of delay for each of these; named such because under a long-standing setup of the DRS, these correspond to about 10,20,30ns of delay after tMax)

tEnd, tStart: The start and end of the pulse defined by setting a noise threshold using the first 100 bins of the event at 2sigma as described for the noise definition. Then, if a pulse is above the noise for 3 consecutive bins, the first bin that went above noise is set as tStart (and similarly for tEnd).

The following parameters are turned off in utils_v9.py but can easily be turned back on by uncommenting the indicated lines in utils. It uses scipy.find_peaks to find the second, third, fourth peaks in the event, saving their parameters as below. This peakfinding script needs modification if you expect the peaks to be possibly a different sign than the main peak, but if the signs on the pulses agree it works well.

vMaxLate,1,2: vMax for the 1st, 2nd, 3rd pulse after the main pulse
tMaxLate,1,2:  for the 1st, 2nd, 3rd pulse after the main pulse
npulse: number of pulses found after the initial pulse (this and the above can be changed to search over the whole event too)




# drsProcessing
A collection of DRS processing and analysis software

Here I have added a set of processing scripts to be used with the DRS4 (version 5+). There are two processing scripts depending on what your workflow prefers: C++ and python

(RECOMMENDED) PYTHON:
This is the more developed processing chain. There are two scripts: "v8", which is for runs taken at fixed bias voltages, and "scans", which was written to accept a .csv
with bias voltage information to be used during bias voltage sweeps.

Usage:
<<<<<<< HEAD
python3 processMultiBoardBinary_v9.py -b <BINARYFILE> [-o OUTFILE -v BIAS -x TXTDUMPBOOL -w WAVEFORMBOOL]
=======
python processMultiBoardBinary_v4.py -b BINARYFILE [-o OUTFILE -v BIAS -x TXTDUMPBOOL -w WAVEFORMBOOL]
>>>>>>> 361bf18ed97269e9b43124d1d2e49aa60d1b9c6a

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

FOR MULTIPLE PULSE FINDING: In the utils_v8.py and subsequent versions, I have code to find multiple peaks. In v9 onward the code was commented out since it slows the processing a bit, but
				if you want to consider the possibility of more than one pulse appearing in the same channel in your window (e.g. an afterpulse), you can uncomment the lines at
				the bottom of the utils and the root trees will fill with the data from scipy.find_peaks

Direct any questions to Ryan Schmitz (schmitz@ucsb.edu or ryan@cern.ch).
