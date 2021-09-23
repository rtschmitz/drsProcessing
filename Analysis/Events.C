#define Events_cxx
#include "Events.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include "TMath.h"
#include "TFile.h"
#include "TTree.h"
#include "TCanvas.h"
#include "TROOT.h"
#include "TH1F.h"
#include "TH1D.h"
#include "TH2F.h"
#include "TH3F.h"
#include <iostream>
#include <iomanip>
#include <fstream>
#include <cmath>
#include <vector>
#include <string>
#include "TString.h"
#include "TVector3.h"
using namespace std;

void tree1r(TChain *fChain)
{
  TFile *outFile = new TFile("Hists.root","UPDATE");
  outFile->cd();

  TH1D *h_Evt1;
  h_Evt1 = new TH1D("Evt1","Time",1024,0.,1023.);
  TH1D *h_Evt2;
  h_Evt2 = new TH1D("Evt2","Time",1024,0.,1023.);
  TH1D *h_Evt3;
  h_Evt3 = new TH1D("Evt3","Time",1024,0.,1023.);
  TH1D *h_Evt4;
  h_Evt4 = new TH1D("Evt4","Time",1024,0.,1023.);
  TH1D *h_Evt5;
  h_Evt5 = new TH1D("Evt5","Time",1024,0.,1023.);
  TH1D *h_Evt6;
  h_Evt6 = new TH1D("Evt6","Time",1024,0.,1023.);
  TH1D *h_Evt7;
  h_Evt7 = new TH1D("Evt7","Time",1024,0.,1023.);
  TH1D *h_EvtLarge;
  h_EvtLarge = new TH1D("EvtLarge","Time",1024,0.,1023.);
  bool largefilled = false;

  TH1D *h_Area1;
  h_Area1 = new TH1D("Area1","Channel 1 area",200,0.,20000.);
  TH1D *h_E1;
  h_E1 = new TH1D("E1","Channel 1 energy",200,0.,2000.);
  TH1D *h_V1;
  h_V1 = new TH1D("V1","Channel 1 pulse height",101,0.,505.);
  TH1D *h_V1_Za;
  h_V1_Za = new TH1D("V1_Za","Channel 1 pulse height",100,0.,150.);
  TH1D *h_E1_V;
  h_E1_V = new TH1D("E1_V","Channel 1 energy calculated from pulse height",100,0.,3000.);
  TH2D *h_VvsA1;
  h_VvsA1 = new TH2D("VvsA1","Channel 1 pulse height vs area",100,0.,6000.,60,0.,60.);

  if (fChain == 0) return;
  InitializeChain(fChain);

  Int_t nentries = (Int_t)fChain->GetEntries();

  Long64_t nbytes = 0, nb = 0;
  for(int ia = 0; ia<nentries; ia++){ // Loop over all events
    fChain->GetEntry(ia);
    //cout << ia << " " << vMax_CH1 << " " << tMax_CH1 << " " << area_CH1<<"\n";
    h_Area1->Fill(area_CH1,1.);
    h_V1->Fill(vMax_CH1,1.);
    h_VvsA1->Fill(area_CH1,vMax_CH1,1.);
    h_V1_Za->Fill(vMax_CH1,1.);
    float calibA = 200.;
    float calibB = -7.;
    float E1 = calibA*area_CH1/1.E3 + calibB*area_CH1*area_CH1/1.E6;
    h_E1->Fill(E1,1.);
    calibA = 16.89;
    calibB = 0.1038;
    float E1_V = calibA*vMax_CH1 + calibB*vMax_CH1*vMax_CH1;
    h_E1_V->Fill(E1_V,1.);

    if (ia == 1)
     for (int i=0; i<1024; i++) 
      h_Evt1->Fill(1.*i+0.5,voltages_CH1[i]);
    if (ia == 2)
     for (int i=0; i<1024; i++) 
      h_Evt2->Fill(1.*i+0.5,voltages_CH1[i]);
    if (ia == 3)
     for (int i=0; i<1024; i++) 
      h_Evt3->Fill(1.*i+0.5,voltages_CH1[i]);
    if (ia == 4)
     for (int i=0; i<1024; i++) 
      h_Evt4->Fill(1.*i+0.5,voltages_CH1[i]);
    if (ia == 5)
     for (int i=0; i<1024; i++) 
      h_Evt5->Fill(1.*i+0.5,voltages_CH1[i]);
    if (ia == 6)
     for (int i=0; i<1024; i++) 
      h_Evt6->Fill(1.*i+0.5,voltages_CH1[i]);
    if (ia == 7)
     for (int i=0; i<1024; i++) 
      h_Evt7->Fill(1.*i+0.5,voltages_CH1[i]);

    if (vMax_CH1 > 60. && !largefilled) {
     for (int i=0; i<1024; i++) 
      h_EvtLarge->Fill(1.*i+0.5,voltages_CH1[i]);
      largefilled = true;
    }

  }

  outFile->cd();
  outFile->Write();
  outFile->Close();
}
