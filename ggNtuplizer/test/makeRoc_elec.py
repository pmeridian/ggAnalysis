import numpy as np
import ROOT
import os

ROOT.gROOT.SetBatch()
sw = ROOT.TStopwatch()
sw.Start()
var_name = 'sigmaIEtaIEta'

# Input ggNtuple
file_in = ROOT.TFile('plots_elec.root')
h_sig = file_in.Get('h_elec_' + var_name)
h_bkg = file_in.Get('h_fake_' + var_name)

# Output file and any histograms we want
file_out = ROOT.TFile('roc_' + var_name + '.root', 'recreate')

c_roc = ROOT.TCanvas('c_roc', '', 580, 620)
c_roc.SetGrid()
g_roc = ROOT.TGraph()
for i in range(h_sig.GetNbinsX()):
    eff_sig = h_sig.Integral(1, i + 1) / h_sig.Integral()
    eff_bkg = h_bkg.Integral(1, i + 1) / h_bkg.Integral()
    g_roc.SetPoint(i, 1.0 - eff_bkg, eff_sig)
g_roc.GetXaxis().SetRangeUser(0.0, 1.1)
g_roc.GetYaxis().SetRangeUser(0.0, 1.1)
g_roc.GetXaxis().SetTitle('Bkg rej')
g_roc.GetYaxis().SetTitle('Sig eff')
g_roc.SetLineWidth(2)
g_roc.SetMarkerStyle(24)
g_roc.SetTitle(var_name + ' ROC')
g_roc.Draw('ACP')
c_roc.Write()

file_out.Write()
file_out.Close()
