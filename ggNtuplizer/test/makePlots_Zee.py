#! /usr/bin/env python

import argparse

import argparse
parser = argparse.ArgumentParser(description="A simple ttree plotter")
parser.add_argument("-i", "--inputfiles", dest="inputfiles", default=["ggtree_mc_dyJetsToLL.root"], nargs='*', help="List of input ggNtuplizer files")
parser.add_argument("-o", "--outputfile", dest="outputfile", default="plotsZee.root", help="Output file containing plots")
parser.add_argument("-m", "--maxevents", dest="maxevents", type=int, default=-1, help="Maximum number events to loop over")
parser.add_argument('--isMC',dest='isMC',action='store_true',default=False)
parser.add_argument('--EBonly',dest='EBonly',action='store_true',default=False)
parser.add_argument('--highR9',dest='highR9',action='store_true',default=False)
parser.add_argument("-t", "--ttree", dest="ttree", default="ggNtuplizer/EventTree", help="TTree Name")
args = parser.parse_args()

import numpy as np
import ROOT
import os

if os.path.isfile('~/.rootlogon.C'): ROOT.gROOT.Macro(os.path.expanduser('~/.rootlogon.C'))
ROOT.gROOT.SetBatch()
ROOT.gROOT.SetStyle("Plain")
ROOT.gStyle.SetOptStat(000000)
ROOT.gStyle.SetPalette(ROOT.kRainBow)
ROOT.gStyle.UseCurrentStyle()

sw = ROOT.TStopwatch()
sw.Start()

# Input ggNtuple
tchain = ROOT.TChain(args.ttree)
for filename in args.inputfiles: tchain.Add(filename)

# This speeds up processing by only reading the branches (quantities) that we plan to use later
branches = ["nEle", "elePt", "eleEta", "elePhi", "eleEn", "eledPhiAtVtx", "eleHoverE", "eleEoverPInv", "eleConvVeto", "eleSigmaIEtaIEtaFull5x5", "eleIDbit", 
            "eleSCEta", "eleSCPhi", "eleSCRawEn", "eleCalibPt", "eleCalibEn", "eleR9" ]
if ( args.isMC ):
    branches.extend( [ "nMC", "mcPt", "mcEta", "mcPhi", "mcE", "mcPID","mcStatus"] )

tchain.SetBranchStatus("*", 0)
for b in branches:
    tchain.SetBranchStatus(b, 1)

print 'Total number of events: ' + str(tchain.GetEntries())

#histograms we want
histos = {}
histos['h_nEle'] = ROOT.TH1D('h_nEle', 'Number of Electrons', 10 , -0.5, 9.5)
histos['h_nEle_passID'] = ROOT.TH1D('h_nEle_passID', 'Number of Electrons Passing ID', 10 , -0.5, 9.5)
histos['h_elec_pt'] = ROOT.TH1D('h_elec_pt', 'Electron p_{T}', 190, 10.0, 200.0)
histos['h_elec_sigmaIEtaIEta'] = ROOT.TH1D('h_elec_sigmaIEtaIEta', 'Electron #sigma_{i#eta i#eta}', 100, 0.0, 0.1)
histos['h_elec_zmass'] = ROOT.TH1D('h_elec_zmass', 'Z peak;Z Mass (GeV)', 140, 60.0, 130.0)

#Loop over all the events in the input ntuple
for ievent,event in enumerate(tchain):
    if ievent > args.maxevents and args.maxevents != -1: break
    if ievent % 1000 == 0: print 'Processing entry ' + str(ievent)

    histos['h_nEle'].Fill(event.nEle)

    # Loop over all the electrons in an event
    goodEle=[]
    for i in range(event.nEle):
        if (event.elePt[i])<20: continue
        if (event.eleIDbit[i]&2)!=2: continue #Loose (94X) selection
        if abs(event.eleSCEta[i]) > 2.5: continue
        if abs(event.eleSCEta[i]) > 1.442 and abs(event.eleSCEta[i])<1.566: continue
        if args.EBonly and abs(event.eleSCEta[i]) > 1.442: continue
        if args.highR9 and event.eleR9[i] < 0.94: continue

        #fill histograms for electrons passing selections
        histos['h_elec_pt'].Fill(event.elePt[i])
        histos['h_elec_sigmaIEtaIEta'].Fill(event.eleSigmaIEtaIEtaFull5x5[i])
        goodEle.append(i)

    histos['h_nEle_passID'].Fill(len(goodEle))

    if len(goodEle) < 2: 
        continue

    lead_ele_vec = ROOT.TLorentzVector()
    lead_ele_vec.SetPtEtaPhiE(event.eleCalibPt[goodEle[0]], event.eleEta[goodEle[0]], event.elePhi[goodEle[0]], event.eleCalibEn[goodEle[0]])
    sublead_ele_vec = ROOT.TLorentzVector()
    sublead_ele_vec.SetPtEtaPhiE(event.eleCalibPt[goodEle[1]], event.eleEta[goodEle[1]], event.elePhi[goodEle[1]], event.eleCalibEn[goodEle[1]])
    zmass = (lead_ele_vec + sublead_ele_vec).M()
    histos['h_elec_zmass'].Fill(zmass)

# save histograms
fOut=ROOT.TFile(args.outputfile,"RECREATE")
for hn, histo in histos.iteritems():
    if isinstance(histo,ROOT.TH1F):
        histo.SetMinimum(0.001) #allow log plot  
    if isinstance(histo,ROOT.TGraphAsymmErrors): #efficiency 
        histo.SetMinimum(0.)
        histo.SetMaximum(1.1) 
    histo.Write()
fOut.Close()
print "Saved histos in "+args.outputfile

sw.Stop()
print 'Real time: ' + str(round(sw.RealTime() / 60.0,2)) + ' minutes'
print 'CPU time:  ' + str(round(sw.CpuTime() / 60.0,2)) + ' minutes'
