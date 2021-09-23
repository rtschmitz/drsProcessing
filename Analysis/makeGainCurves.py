import sys
import ROOT as rt

inFile = sys.argv[1]
f = rt.TFile.Open(inFile,"READ")
t = f.Events

h20=[]
h30=[]
c1 = rt.TCanvas()
c2 = rt.TCanvas()
c1.cd()
boards = ['2881','2880','2879','2781']
colors = [1,2,3,4,6,7,9,12,15,30,38,42,46,880,820,800]
t.Draw("scan>>htemp(100,0,100)")
hscan = rt.gDirectory.Get("htemp")
n_scans = hscan.FindLastBinAbove(0)
scanNum=2;
n_boards = 4
n_chans = 4
rt.gStyle.SetOptStat(0)
goodHistos = 0
goodHistos10 = 0
maxY = 0
maxRatio = 0
minRatio = 0
h = [[[None for i in range(n_chans)] for j in range (n_boards)] for k in range (n_scans)]
h10 = [[[None for i in range(n_chans)] for j in range (n_boards)] for k in range (n_scans)]
for iscn in range(n_scans):
    for ibd in range(n_boards):
        for ichn in range(n_chans):
            t.Draw("area_"+boards[ibd]+"_"+str(ichn+1)+":bias_voltage>>htemp"+str(ibd)+str(ichn+1)+str(iscn)+"(300,0,300)","scan=="+str(iscn)+"&&area_"+boards[ibd]+"_"+str(ichn+1)+">0","prof")
            h[iscn][ibd][ichn] = rt.gDirectory.Get("htemp"+str(ibd)+str(ichn+1)+str(iscn))
            t.Draw("vFix10_"+boards[ibd]+"_"+str(ichn+1)+":bias_voltage>>htemp10_"+str(ibd)+str(ichn+1)+str(iscn)+"(300,0,300)","scan=="+str(iscn),"prof")
            h10[iscn][ibd][ichn] = rt.gDirectory.Get("htemp10_"+str(ibd)+str(ichn+1)+str(iscn))
            h[iscn][ibd][ichn] = h[iscn][ibd][ichn].ProjectionX()
            h10[iscn][ibd][ichn] = h10[iscn][ibd][ichn].ProjectionX()
            goodHistos+=1

for iscn in range(n_scans):
    for ibd in range(n_boards):
        for ichn in range(n_chans):
            h[iscn][ibd][ichn].SetMarkerStyle(25); h10[iscn][ibd][ichn].SetMarkerStyle(25)
            h[iscn][ibd][ichn].SetMarkerSize(0.5); h10[iscn][ibd][ichn].SetMarkerSize(0.5)
            h[iscn][ibd][ichn].SetMarkerColor(colors[ibd*n_chans+ichn]); h10[iscn][ibd][ichn].SetMarkerColor(colors[ibd*n_chans+ichn])
            if(iscn==n_scans-2 and ibd==3 and ichn==3):
                h[iscn][ibd][ichn].SetTitle("Gain curves for channels on 5x5 sensor")
                h[iscn][ibd][ichn].GetXaxis().SetTitle("Bias voltage [-V]")
                h[iscn][ibd][ichn].GetYaxis().SetTitle("Pulse area [pV.s]")
                h10[iscn][ibd][ichn].SetTitle("Gain curves for channels on 5x5 sensor")
                h10[iscn][ibd][ichn].GetXaxis().SetTitle("Bias voltage [-V]")
                h10[iscn][ibd][ichn].GetYaxis().SetTitle("Voltage at 10ns [mV]")
                try:
                    h[iscn][ibd][ichn].Scale(200.0/h[iscn][ibd][ichn].GetBinContent(111))
                    maxY = max(maxY,h[iscn][ibd][ichn].GetMaximum()+100)
                except:
                    continue
                try:
                    h10[iscn][ibd][ichn].Scale(10.0/h10[iscn][ibd][ichn].GetBinContent(111))
                    maxRatio = max(maxRatio,h10[iscn][ibd][ichn].GetMaximum()+5.)
                except:
                    continue
            else:
                try:
                    h[iscn][ibd][ichn].Scale(200.0/h[iscn][ibd][ichn].GetBinContent(111))
                    maxY = max(maxY,h[iscn][ibd][ichn].GetMaximum()+100)
                except:
                    continue
                try:
                    h10[iscn][ibd][ichn].Scale(10.0/h10[iscn][ibd][ichn].GetBinContent(111))
                    maxRatio = max(maxRatio,h10[iscn][ibd][ichn].GetMaximum()+5.)
                except:
                    continue

h[n_scans-2][3][3].GetYaxis().SetRangeUser(0,maxY)
h10[n_scans-2][3][3].GetYaxis().SetRangeUser(0,maxRatio)
c1.cd()
h[n_scans-2][3][3].Draw()
c2.cd()
h10[n_scans-2][3][3].Draw()
for iscn in range(n_scans):
    for ibd in range(n_boards):
        for ichn in range(n_chans):
            if not(iscn==n_scans-2 and ibd==3 and ichn==3):
                c1.cd()
                h[iscn][ibd][ichn].Draw("SAME")
                c2.cd()
                h10[iscn][ibd][ichn].Draw("SAME")
c1.Update(); c2.Update()
#c1.WaitPrimitive()
c1.SaveAs("testcanvas.png"); c2.SaveAs("testcanvas10.png")
