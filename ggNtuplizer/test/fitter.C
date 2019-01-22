void fitter (TString filename = "plots.root", TString plotSuffix = "", float startmass = 91.1876) {
  using namespace RooFit;

  //  gStyle->SetOptStat(0);
  gStyle->SetPalette(1);
  gROOT->SetStyle("Plain");
  gStyle->SetPadLeftMargin(0.15);
  gStyle->SetTitleOffset(1.8,"y");
  gStyle->SetTitleW(.54);
  TCanvas * c1 = new TCanvas("c1", "c1",430, 10, 800, 800);
  c1->SetBorderMode(0);
  
  //Parameter used for mass in both CrystalBall or BreitWigner
  RooRealVar mass("mass","m_{ee}", 70, 130,"GeV/c^{2}");

  //Parameters for Crystal Ball Lineshape 
  RooRealVar m0("#DeltaM_{Z}", "Bias", 0, -1., 1);//,"GeV/c^{2}"); 
  RooRealVar sigma("#sigma_{CB}","Width", 1.2,0.1,10);//,"GeV/c^{2}"); 
  RooRealVar cut("#alpha","Cut", 1., 0., 10.); 
  RooRealVar power("#gamma","Power", 1., 0., 10.); 
  RooCBShape CrystalBall("CrystalBall", "A  Crystal Ball Lineshape", mass, m0,sigma, cut, power);
            
  //Parameters for Breit-Wigner Distribution
  RooRealVar mRes("M_{Z}", "Z Resonance  Mass", startmass);//,"GeV/c^{2}"); 
  RooRealVar Gamma("#Gamma_{Z}", "#Gamma", 2.4952);//,"GeV/c^{2}");
  RooBreitWigner BreitWigner("BreitWigner","A Breit-Wigner Distribution",mass,mRes,Gamma);

  //Convoluve the BreitWigner and Crystal Ball
  RooFFTConvPdf ResolutionModel("Convolution","Convolution", mass, BreitWigner,  CrystalBall);

  TFile * hFile = new TFile(filename.Data());
  TH1F * DataHist = (TH1F*) hFile->Get("h_elec_zmass");
  DataHist->UseCurrentStyle();
  TString DataHistName = DataHist->GetName();
  DataHistName += "fit";
  RooDataHist data(DataHistName,DataHistName,mass,DataHist);
  ResolutionModel.fitTo(data,Range(startmass-15,startmass+10));
  RooPlot * plot = mass.frame();
  data.plotOn(plot);
  plot->SetMaximum(1.2*plot->GetMaximum());
  ResolutionModel.plotOn(plot);
  ResolutionModel.paramOn(plot,Format("NEL",AutoPrecision(1)), Parameters(RooArgSet(m0, sigma, cut, power, mRes, Gamma)), Layout(.15, 0.4, 0.9), ShowConstants(kFALSE));
  TString PlotTitle(DataHist->GetTitle());
  PlotTitle += ";m_{ee} (GeV/c^{2});Number of Weighted Events";
  plot->SetTitle(PlotTitle);
  plot->GetXaxis()->SetRangeUser(startmass-15,startmass+10);
  TPaveText *box = (TPaveText*) plot->findObject("Convolution_paramBox");
  box->SetTextSize(0.022);
  plot->Draw();
  TString ext[2] = { ".png" , ".pdf"};
  for (int iext=0;iext<2;++iext)
    {
      TString OutPutName = Form("%s_%s%s",DataHist->GetName(),plotSuffix.Data(),ext[iext].Data());
      c1->SaveAs(OutPutName);
    }
}
