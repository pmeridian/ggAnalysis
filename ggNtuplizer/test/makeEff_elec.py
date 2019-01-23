import numpy as np
import ROOT
import os
import argparse
import math as M

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

# Fill dictionary with histograms from inputs
histos={}
for key, value in f.iteritems():
    histos[key]=Map(value)

#print histos
sel =  [ 'eleID' ] #first item is supposed to be the reference selection, in this case no selection

c_eff = ROOT.TCanvas('c_eff', '', 580, 620)
c_eff.SetGrid()

g_roc={}

ranges={}
ranges['pt']=[ 20, 70. ]
ranges['eta']=[ 0. , 3. ]
ranges['phi']=[ -M.pi , M.pi ]

axisT={}
axisT['pt']= 'p_{T} [GeV]' 
axisT['eta']= '#eta' 
axisT['phi']= '#phi' 


for var_name in sel:
    for det in ['EB','EE']:
        for t in [ 'pt','eta', 'phi']:
            
            g_roc[det+'_'+t+'_'+var_name] = ROOT.TGraphAsymmErrors( histos['sig']['h_eleMC_'+det+'_'+t+'_'+var_name], histos['sig']['h_eleMC_'+det+'_'+t])
            g_roc[det+'_'+t+'_'+var_name].GetXaxis().SetRangeUser(ranges[t][0],ranges[t][1])
            g_roc[det+'_'+t+'_'+var_name].GetYaxis().SetRangeUser(0.,1.2)
            g_roc[det+'_'+t+'_'+var_name].GetXaxis().SetTitle(axisT[t])
            g_roc[det+'_'+t+'_'+var_name].GetYaxis().SetTitle('Efficiency')
            g_roc[det+'_'+t+'_'+var_name].SetLineWidth(2)
            g_roc[det+'_'+t+'_'+var_name].SetMarkerStyle(24)
            g_roc[det+'_'+t+'_'+var_name].SetTitle( 'Eff vs '+ t + ' ('+det+')' )
            g_roc[det+'_'+t+'_'+var_name].Draw('AP')
            saveCanvas(c_eff,'eff_' + det + '_' + t + '_' + var_name)
