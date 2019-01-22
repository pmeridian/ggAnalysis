import numpy as np
import ROOT
import os
import argparse

def Map(tf):
    """                                                                                                                                      
    Maps objets as dict[obj_name][0] using a TFile (tf) and TObject to browse.                                                               
    """
    m = {}
    for k in tf.GetListOfKeys():
        n = k.GetName()
        m[n] = tf.Get(n)
    return m

def saveCanvas(c,n):
    defaultTitle(0.1,0.91,args.title)
    for ext in ['.png','.pdf','.root' ]:
        c.SaveAs(args.output+"/"+n+ext)

def defaultTitle(x,y,text):
    t=ROOT.TLatex()
    t.SetTextSize(0.035)
    t.DrawLatexNDC(x,y,text)

parser = argparse.ArgumentParser()
parser.add_argument('--output',dest='output')
parser.add_argument('--title',dest='title')
args = parser.parse_args()

if not os.path.exists(args.output): 
    print('Creating dir '+args.output)
    os.makedirs(args.output) 

ROOT.gROOT.SetBatch()
#R.gROOT.LoadMacro("tdrstyle.C")
#R.gInterpreter.ProcessLine('setTDRStyle()')

sw = ROOT.TStopwatch()
sw.Start()

f={}

# Inputs
f['sig']=ROOT.TFile('elePlots_DY.root')
f['bkg']=ROOT.TFile('elePlots_TTJets.root')

# Fill dictionary with histograms from inputs
histos={}
for key, value in f.iteritems():
    histos[key]=Map(value)

#print histos
vars =  [ 'sigmaIEtaIEta' ]

c_roc = ROOT.TCanvas('c_roc', '', 580, 620)
c_roc.SetGrid()

h_sig={}
h_bkg={}
g_roc={}

for var_name in vars:
    for det in ['EB','EE']:
        h_sig[det + '_' + var_name] = histos['sig']['h_eleMC_'   + det + '_' +var_name]
        h_bkg[det + '_' + var_name] = histos['bkg']['h_eleFake_' + det + '_' +var_name]
        g_roc[det + '_' + var_name] = ROOT.TGraph()
        for i in range(h_sig[det + '_' + var_name].GetNbinsX()): #assumes here a cut var>cut
            eff_sig = h_sig[det + '_' + var_name].Integral(1, i + 1) / h_sig[det + '_' + var_name].Integral()
            eff_bkg = h_bkg[det + '_' + var_name].Integral(1, i + 1) / h_bkg[det + '_' + var_name].Integral()
            g_roc[det + '_' + var_name].SetPoint(i, 1.0 - eff_bkg, eff_sig)
        g_roc[det + '_' + var_name].GetXaxis().SetRangeUser(0.0, 1.1)
        g_roc[det + '_' + var_name].GetYaxis().SetRangeUser(0.0, 1.1)
        g_roc[det + '_' + var_name].GetXaxis().SetTitle('Bkg rej')
        g_roc[det + '_' + var_name].GetYaxis().SetTitle('Sig eff')
        g_roc[det + '_' + var_name].SetLineWidth(2)
        g_roc[det + '_' + var_name].SetMarkerStyle(24)
        g_roc[det + '_' + var_name].SetTitle(var_name + ' ROC')
        g_roc[det + '_' + var_name].Draw('ACP')
        saveCanvas(c_roc,'roc_' + det + '_' + var_name)
