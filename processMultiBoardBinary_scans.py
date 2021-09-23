#! /usr/bin/env python

# take a binary file output from DRS scope
# create a ROOT file with time and voltage arrays
##
# note that time values are different for every event since
# DRS binning is uneven, and the trigger can occur in any bin

import os
import sys
import struct
import datetime as dt
import json
import csv
import glob
import argparse
import numpy as np
import ROOT as r
import time
from multiprocessing import Pool
from utils_v4 import *

def processMultiChanBinary(name, HV=[], currs=[], uts=[], waveFlag=False):
    print("Processing " + name)
    indir = str(inpath)
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    outdir = str(outpath)
        
    N_BINS = 1024  # number of timing bins per channel

    fin = indir+"/{0}.dat".format(name)
    fout = r.TFile(outdir+"/{0}.root".format(name), "RECREATE")
    if waveFlag:
        time_arr = {}
        voltage_arr = {}
    area_arr = {}
    width_arr = {}
    offset_arr = {}
    noise_arr = {}
    
    trig_cell = np.array([0], dtype=int)
    evtHV = np.array([0], dtype=float)
    evtHV_adj = np.array([0], dtype=float)
    evtCurr = np.array([0], dtype=float)
    scan = np.array([0], dtype=int)

    vMax_arr = {}
    vMaxEarly_arr = {}
    vMinEarly_arr = {}
    tMax_arr = {}
    vFix10_arr = {}
    vFix20_arr = {}
    vFix30_arr = {}
    
    t = r.TTree("Events", "Events")
    if len(HV) > 0 or len(uts) > 0:
    	eHV = t.Branch("bias_voltage", evtHV, 'bias/D')
    	eHV_adj = t.Branch("bias_voltage_adjusted", evtHV_adj, 'adjusted_bias/D')
    	eCurr = t.Branch("bias_current", evtCurr, 'bias/D')
    b_scan = t.Branch("scan_number", scan, 'scan/I')

    fid = open(fin, 'rb')

    # make sure file header is correct
    fhdr = getStr(fid, 4)
    if fhdr != "DRS2":
        print("ERROR: unrecognized header "+fhdr)
        exit(1)

    # make sure timing header is correct
    thdr = getStr(fid, 4)
    if thdr != "TIME":
        print("ERROR: unrecognized time header "+thdr)
        exit(1)

    # get the boards in file
    n_boards = 0
    n_chans = 0
    channels = []
    board_ids = []
    bin_widths = []
    while True:
        bhdr = getStr(fid, 2)
        if bhdr != "B#":
            fid.seek(-2, 1)
            break
        board_ids.append(getShort(fid))
        n_boards += 1
        bin_widths.append([])
        channels.append([])
        print("Found Board #"+str(board_ids[-1]))
        
        while True:
            test = getStr(fid, 2)
            if test == "C0":
                fid.seek(-2, 1)
                chdr = getStr(fid, 3)
            else:
                fid.seek(-2, 1)
                break
            if chdr != "C00":
                fid.seek(-3, 1)
                break
            cnum = int(getStr(fid, 1))
            print("Found channel #"+str(cnum))
            n_chans += 1
            channels[n_boards-1].append(cnum)
            binw = getFloat(fid,N_BINS)
            bin_widths[n_boards-1].append(binw)

        if len(bin_widths[n_boards-1]) == 0:
            print("ERROR: Board #{0} doesn't have any channels!".format(
                board_ids[-1]))

    #print(channels)
    if n_boards == 0:
        print("ERROR: didn't find any valid boards!")
        exit(1)

    #if n_boards > 1:
    #    print(
    #        "ERROR: only support one board. Found {0} in file.".format(n_boards))
    #    exit(1)

    bin_widths = bin_widths[0]
    rates = []
    for ibd in range(len(board_ids)):
        for ichn in range(len(channels[ibd])):
            id_chn = str(board_ids[ibd])+'_'+str(channels[ibd][ichn])
            if waveFlag:
                time_arr[id_chn] = np.zeros(1024, dtype=float)
                voltage_arr[id_chn] = np.zeros(1024, dtype=float)
                t.Branch("times_"+id_chn,time_arr[id_chn],"times_"+id_chn+"[1024]/D")
                t.Branch("voltages_"+id_chn,voltage_arr[id_chn],"voltages_"+id_chn+"[1024]/D")
            area_arr[id_chn] = np.array([0], dtype=float)
            width_arr[id_chn] = np.array([0], dtype=float)
            offset_arr[id_chn] = np.array([0], dtype=float)
            noise_arr[id_chn] = np.array([0], dtype=float)
            vMax_arr[id_chn] = np.array([0], dtype=float)
            vMaxEarly_arr[id_chn] = np.array([0], dtype=float)
            vMinEarly_arr[id_chn] = np.array([0], dtype=float)
            tMax_arr[id_chn] = np.array([0], dtype=float)
            vFix10_arr[id_chn] = np.array([0], dtype=float)
            vFix20_arr[id_chn] = np.array([0], dtype=float)
            vFix30_arr[id_chn] = np.array([0], dtype=float)
            t.Branch("area_"+id_chn,area_arr[id_chn],"area_"+id_chn+"/D")
            t.Branch("width_"+id_chn,width_arr[id_chn],"width"+id_chn+"/D")
            t.Branch("offset_"+id_chn,offset_arr[id_chn],"offset_"+id_chn+"/D")
            t.Branch("noise_"+id_chn,noise_arr[id_chn],"noise_"+id_chn+"/D")
            t.Branch("vMax_"+id_chn,vMax_arr[id_chn],"vMax_"+id_chn+"/D")
	    t.Branch("vMaxEarly_"+id_chn,vMaxEarly_arr[id_chn],"vMaxEarly_"+id_chn+"/D")
            t.Branch("vMinEarly_"+id_chn,vMinEarly_arr[id_chn],"vMinEarly_"+id_chn+"/D")
            t.Branch("tMax_"+id_chn,tMax_arr[id_chn],"tMax_"+id_chn+"/D")
            t.Branch("vFix10_"+id_chn,vFix10_arr[id_chn],"vFix10_"+id_chn+"/D")
            t.Branch("vFix20_"+id_chn,vFix20_arr[id_chn],"vFix20_"+id_chn+"/D")
            t.Branch("vFix30_"+id_chn,vFix30_arr[id_chn],"vFix30_"+id_chn+"/D")

    epoch = dt.datetime.utcfromtimestamp(0)
    #-7 for March - November Daylight Savings Time, -8 otherwise for Standard Time
    UTC_OFFSET = -7
    #UTC_OFFSET = -8

    n_evt = 0
    bad_evt = 0
    lastHV = 0
    n_scan = 0
    scan_up = True
    start_row = 2
    while True:
        ehdr = getStr(fid, 4)
        if ehdr is None:
            break
        if ehdr != 'EHDR':
            raise Exception("Bad event header!")

        n_evt += 1
        # skip 2 digits for NO USE
        serial = getInt(fid)

        # print "  Serial #"+str(serial)
        # Following lines get event time convert to UNIX timestamp
        # Quick cheat to get from PST to UTC but doesn't account for daylight savings...
        date = getShort(fid, 7)
        date = dt.datetime(*date[:6], microsecond=1000*date[6])
        date = date - dt.timedelta(hours=UTC_OFFSET)
        timestamp = (date - epoch).total_seconds()
        # argmax(uts>timestamp) returns the index when
        # event time (timestamp) comes before a uts voltage change time
        # so the voltage of event corresponds to the previous argument
        # since it is the bin where timestamp occurred (> lower limit, < upper)
        if len(uts) > 0:
            if(timestamp<uts[0]):
                print("Warning! Event "+str(n_evt)+" before first Keithley time!")
            elif(timestamp>uts[-1]):
                print("Warning! Event "+str(n_evt)+" after last Keithley time!")
            nextChange = np.argmax(uts > timestamp)
            previous = nextChange-1
            gap = uts[nextChange] - uts[previous]
            lastHV = evtHV[0]
            evtHV[0] = HV[np.argmax(uts > timestamp)-1]
            evtHV_adj[0] = HV[np.argmax(uts > timestamp)-1] - 1.1e6*currs[np.argmax(uts > timestamp)-1]
            evtCurr[0] = currs[np.argmax(uts > timestamp)-1]
        
        if scan_up and evtHV[0] < lastHV:
            n_scan += 1
            scan_up = False
            scan[0] = n_scan
        elif (not scan_up) and evtHV[0] > lastHV:
            n_scan += 1
            scan_up = True
            scan[0] = n_scan
        else:
            scan[0] = n_scan

        if((n_evt-1) % 10000 == 0):
            print("Processing event "+str(n_evt-1))
            sys.stdout.flush()

        if n_evt == 1:
            t_start = date
        t_end = date
        # print "  Date: "+str(date)
        rangeCtr = getShort(fid)
        # print "  Range Center: "+str(rangeCtr)
        for ibd in range(n_boards):
            getStr(fid, 2)
            b_num = getShort(fid)
            getStr(fid, 2)
            trig_cell[0] = getShort(fid)
            # print "  Trigger Cell: "+str(trig_cell)


            goodFlag = True
            for ichn in range(len(channels[ibd])):
                chdr = getStr(fid, 4)
                if chdr != "C00"+str(channels[ibd][ichn]):
                    print("ERROR: bad event data!")
                    exit(1)

                id_chn = str(board_ids[ibd])+'_'+str(channels[ibd][ichn])
                # skipping digits again
                scaler = getInt(fid)
                voltages = np.array(getShort(fid, N_BINS))
                # if READ_CHN != channels[ichn]:
                #    continue
                # if (timestamp > (uts[nextChange] - 0.2*gap)):
                #     goodFlag = False
                #     continue
                voltages = voltages/65535. * 1000 - 500 + rangeCtr
                times = np.roll(np.array(bin_widths[ichn]), N_BINS-trig_cell[0])
                times = np.cumsum(times)
                times = np.append([0], times[:-1])
                rates.append((times[-1]-times[0])/(times.size-1))
                try:
                    area, width, offset, noise, tMax, vMax, vMaxEarly, vMinEarly, vFix10, vFix20, vFix30 = postprocess(voltages, times)
                except:
                #if ichn == 0:
                    #    print("ERROR: bad event "+str(n_evt-1))
                    #    bad_evt += 1
                    continue
                # area, offset, noise, tMax, vMax = 0,0,0,0,0
                if waveFlag:
                    np.copyto(voltage_arr[id_chn], voltages)
                    np.copyto(time_arr[id_chn], times)
                np.copyto(area_arr[id_chn], area)
                np.copyto(width_arr[id_chn], width)
                np.copyto(offset_arr[id_chn], offset)
                np.copyto(noise_arr[id_chn], noise)
                np.copyto(tMax_arr[id_chn], tMax)
                np.copyto(vMax_arr[id_chn], vMax)
                np.copyto(vMaxEarly_arr[id_chn], vMaxEarly)
                np.copyto(vMinEarly_arr[id_chn], vMinEarly)
                np.copyto(vFix10_arr[id_chn], vFix10)
                np.copyto(vFix20_arr[id_chn], vFix20)
                np.copyto(vFix30_arr[id_chn], vFix30)    
            #if goodFlag:
            t.Fill()

    t_tot = t_end - t_start
    t_sec = t_tot.total_seconds()

    print("Measured sampling rate: {0:.2f} GHz".format(1.0/np.mean(rates)))
    print("Total time of run = " + str(t_tot) +
          " = " + str(t_sec) + " seconds.")
    print("Event rate = " + str(n_evt/t_sec) + " Hz")
    t.Write()
    fout.Close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse DRS .dat file and .csv into .root files")
    parser.add_argument('-b', '--binaryfile',
                        help='Path to binary files', required=True, type=str)
    parser.add_argument('-o', '--outputpath',
                        help='Path for output ROOT file', required=False, type=str)
    parser.add_argument('-c', '--csvpath', 
                        help='Path to folder of CSV file', required=False, type=str)
    parser.add_argument('-w', '--waveform',
                        help='Bool to add all waveforms to root output', required=False, type=bool)
    args = vars(parser.parse_args())

    datfiles = glob.glob(args["binaryfile"])
    #datfiles = glob.glob(args["binaryfile"]+"*.dat")
    try:
        csvpath = glob.glob(args['csvpath'])
        #csvpath = glob.glob(args['csvpath']+"*.csv")
    except TypeError:
        csvpath = []
    outpath = args['outputpath']
    waveFlag = args['waveform']
    if outpath == None:
        outpath = "./processed/"

    HV, currs, uts = parseCSV(csvpath)
    poolargs = []
    for each in datfiles:
        folder, name = each.rsplit('/', 1)
        name, ext = name.rsplit('.', 1)
        # avoid overwrite
        if not (glob.glob(outpath+name+".root")):
            #poolargs.append((name, HV, currs, uts))
            prog_start = dt.datetime.now()
            inpath = folder
            processMultiChanBinary(name, HV, currs, uts, waveFlag)
            print("Time to process = "+str(dt.datetime.now()-prog_start))
    #pool = Pool(processes=5)
    #pool.starmap(processMultiChanBinary, poolargs)
