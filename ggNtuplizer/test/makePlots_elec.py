import ROOT
import os
import math as M
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input',dest='input')
parser.add_argument('--output',dest='output')
parser.add_argument('--events',dest='events')
parser.add_argument('--isMC',dest='isMC',action='store_true',default=False)
args = parser.parse_args()

etaAcceptance = {} # fiducial region
etaAcceptance['EB']= [ 0. , 1.442 ] 
etaAcceptance['EE']= [ 1.566 , 2.5 ]

# Function to check if the electron belongs to ECAL barrel (EB) or endcap (EE)
def eleDet(iEle):
    for det in ['EB','EE']:
        if ( 
            abs(chain_in.eleSCEta[iEle]) >= etaAcceptance[det][0]
            and abs(chain_in.eleSCEta[iEle]) < etaAcceptance[det][1]  
            ):
            return det
    return 'OOA' #out of acceptance

# Function to check if a reconstructed electron is matched to a generator electron
def has_mcEle_match(iEle):
    ele_vec = ROOT.TLorentzVector()
    ele_vec.SetPtEtaPhiE(chain_in.elePt[iEle], chain_in.eleEta[iEle],
                         chain_in.elePhi[iEle], chain_in.eleEn[iEle])

    for mc in range(chain_in.nMC):
        if abs(chain_in.mcPID[mc]) != 11 or chain_in.mcPt[mc] < 15. or chain_in.mcStatus[mc]!=1:
            continue
        mc_vec = ROOT.TLorentzVector()
        mc_vec.SetPtEtaPhiE(chain_in.mcPt[mc], chain_in.mcEta[mc], chain_in.mcPhi[mc], chain_in.mcE[mc])
        delta_r = ele_vec.DeltaR(mc_vec)
        if delta_r < 0.05:
            return True
    return False

# return the class for the electron ['eleMC', 'eleFake' ] for MC [ 'eleData' ] in Data
def eType(iEle): 
    if (args.isMC):
        if (has_mcEle_match(iEle)):
            return "eleMC"
        else:
            return "eleFake"
    else:
        return "eleData"

sw = ROOT.TStopwatch()
sw.Start()

#return tighest level of cutBased eleID passed by the electron manipulating eleIDbit from ntuple
def eleID(eleIDbit):
    #bit 0 cutBasedElectronID-Fall17-94X-V1-veto 
    #bit 1 cutBasedElectronID-Fall17-94X-V1-loose 
    #bit 2 cutBasedElectronID-Fall17-94X-V1-medium 
    #bit 3 cutBasedElectronID-Fall17-94X-V1-tight 
    for i in range(3,-1,-1):
        if (eleIDbit>>i&1): #checks the i-th bit of the eleID bit starting from the MSB
            return i+1
    return 0
        
max_entries = -1 if args.events is None else int(args.events)

# Input ggNtuple
chain_in = ROOT.TChain('ggNtuplizer/EventTree')
chain_in.Add(args.input)

# This speeds up processing by only reading the branches (quantities) that we plan to use later
branches = ["nEle", "elePt", "eleEta", "elePhi", "eleEn", "eledPhiAtVtx", "eleHoverE", "eleEoverPInv", "eleConvVeto", "eleSigmaIEtaIEtaFull5x5",
            "eleSCEta", "eleSCPhi", "eleSCRawEn", "eleIDbit","eleIDMVAIso" ]
if ( args.isMC ):
    branches.extend( [ "nMC", "mcPt", "mcEta", "mcPhi", "mcE", "mcPID","mcStatus"] )

chain_in.SetBranchStatus("*", 0)
for b in branches:
    chain_in.SetBranchStatus(b, 1)

n_entries = chain_in.GetEntries()
print 'Total number of events: ' + str(n_entries) + " Limit: " + str(max_entries)

eleTypes = []
if ( args.isMC):
    eleTypes.extend(['eleMC' , 'eleFake'])
else:
    eleTypes.extend(['eleData'])

histos = {}
for eleType in eleTypes:
    for det in ['EB','EE']:
        histos['h_'+eleType+'_'+det+'_pt']            = ROOT.TH1D('h_'+eleType+'_'+det+'_pt', 'Electron p_{T}', 190, 10.0, 200.0)
        histos['h_'+eleType+'_'+det+'_eta']            = ROOT.TH1D('h_'+eleType+'_'+det+'_eta', 'Electron #eta', 50, 0., 2.5)
        histos['h_'+eleType+'_'+det+'_phi']            = ROOT.TH1D('h_'+eleType+'_'+det+'_phi', 'Electron #phi', 100, -M.pi, M.pi)
        histos['h_'+eleType+'_'+det+'_sigmaIEtaIEta'] = ROOT.TH1D('h_'+eleType+'_'+det+'_sigmaIEtaIEta', 'Electron #sigma_{i#eta i#eta}', 100, 0.0, 0.1)
        histos['h_'+eleType+'_'+det+'_eleID']            = ROOT.TH1D('h_'+eleType+'_'+det+'_eleID', 'Electron ID (cut based)', 10, -0.5, 9.5)
        histos['h_'+eleType+'_'+det+'_eleIDMVA']            = ROOT.TH1D('h_'+eleType+'_'+det+'_eleIDMVA', 'Electron ID (MVA)', 100, -1., 1.)
        histos['h_'+eleType+'_'+det+'_pt'+'_eleID']            = ROOT.TH1D('h_'+eleType+'_'+det+'_pt'+'_eleID', 'Electron p_{T}', 190, 10.0, 200.0)
        histos['h_'+eleType+'_'+det+'_eta'+'_eleID']            = ROOT.TH1D('h_'+eleType+'_'+det+'_eta'+'_eleID', 'Electron #eta', 50, 0., 2.5)
        histos['h_'+eleType+'_'+det+'_phi'+'_eleID']            = ROOT.TH1D('h_'+eleType+'_'+det+'_phi'+'_eleID', 'Electron #phi', 100, -M.pi, M.pi)

#Loop over all the events in the input ntuple
for j_entry in range(min(max_entries,n_entries) if max_entries>0 else n_entries):
    i_entry = chain_in.LoadTree(j_entry)
    if i_entry < 0:
        break
    nb = chain_in.GetEntry(j_entry)
    if nb <= 0:
        continue

    if j_entry % 1000 == 0:
        print 'Processing entry ' + str(j_entry)

    # Loop over all the electrons in an event
    for i in range(chain_in.nEle):
        if (chain_in.elePt[i] < 20. ):
            continue
        ele_det=eleDet(i)
        ele_type=eType(i) 

        #fill reconstructed electron kinematics
        if (not ele_det == 'OOA'):
            histos['h_'+ele_type+'_'+ele_det+'_pt'].Fill(chain_in.elePt[i])
            histos['h_'+ele_type+'_'+ele_det+'_eta'].Fill(chain_in.eleEta[i])
            histos['h_'+ele_type+'_'+ele_det+'_phi'].Fill(chain_in.elePhi[i])

        if ( #apply a simple and very loose preselection here
            ( 
                (ele_det=='EB' #EB very loose preselection
                 and abs(chain_in.eledPhiAtVtx[i]) < 0.2
                 and chain_in.eleHoverE[i] < 0.1
                 and abs(chain_in.eleEoverPInv[i]) < 0.3
                 and chain_in.eleConvVeto[i] == 1 
                 )
                or
                (ele_det=='EE' #EE very loose preselection
                 and abs(chain_in.eledPhiAtVtx[i]) < 0.25
                 and chain_in.eleHoverE[i] < 0.15
                 and abs(chain_in.eleEoverPInv[i]) < 0.2
                 and chain_in.eleConvVeto[i] == 1 
                 )
                )
            ):
            histos['h_'+ele_type+'_'+ele_det+'_sigmaIEtaIEta'].Fill(chain_in.eleSigmaIEtaIEtaFull5x5[i])
            histos['h_'+ele_type+'_'+ele_det+'_eleID'].Fill(eleID(chain_in.eleIDbit[i])) 
            histos['h_'+ele_type+'_'+ele_det+'_eleIDMVA'].Fill(chain_in.eleIDMVAIso[i]) 

            #store kinematic for efficiency plots 
            if (eleID(chain_in.eleIDbit[i])>1): # pass cutBasedElectronID-Fall17-94X-V2-loose
                histos['h_'+ele_type+'_'+ele_det+'_pt'+'_eleID'].Fill(chain_in.elePt[i])
                histos['h_'+ele_type+'_'+ele_det+'_eta'+'_eleID'].Fill(chain_in.eleEta[i])
                histos['h_'+ele_type+'_'+ele_det+'_phi'+'_eleID'].Fill(chain_in.elePhi[i])
                
# save histograms
fOut=ROOT.TFile(args.output,"RECREATE")
for hn, histo in histos.iteritems():
    if isinstance(histo,ROOT.TH1F):
        histo.SetMinimum(0.001) #allow log plot  
    if isinstance(histo,ROOT.TGraphAsymmErrors): #efficiency 
        histo.SetMinimum(0.)
        histo.SetMaximum(1.1) 
    histo.Write()
fOut.Close()
print "Saved histos in "+args.output

sw.Stop()
print 'Real time: ' + str(sw.RealTime() / 60.0) + ' minutes'
print 'CPU time:  ' + str(sw.CpuTime() / 60.0) + ' minutes'

