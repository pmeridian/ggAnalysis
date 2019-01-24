#### Current production tag : 
#### Newest tag for testing : 
#### This version can be run using CMSSW_9_4_10

##### To work with CMSSW_9_4_10:
```Shell
cmsrel CMSSW_9_4_10
cd CMSSW_9_4_10/src
cmsenv
git cms-init
git clone https://github.com/cmkuo/HiggsAnalysis.git
git clone -b cmsdas2019 https://github.com/pmeridian/ggAnalysis.git
git cms-merge-topic cms-egamma:EgammaPostRecoTools_940
git cms-merge-topic cms-egamma:EgammaID_949
git cms-merge-topic cms-met:METFixEE2017_949
scram b -j 8
```
Test ntuples production: <br>
```Shell
cd ggAnalysis/ggNtuplizer/test/
cmsRun run_2017_94x.py datasets=/DoubleEG/Run2017F-31Mar2018-v1/MINIAOD runs=306092 output=DoubleEG.root maxEvents=1000
```
Some informations on stored IDs.<br> <br>
eleID is stored in 64bit integer. Each bit represents the output of an ID selections<br>
for ELECRON ID stores 5 official 94x ID outputs: 5 IDs (Veto, Loose, Medium, Tight and HEEP) so only 5 bits are imp for us (59 bits of this integer  we are not using so may be we can change that to 16 bit integer later)<br>
Representing that integer in 5 bits: b4 b3 b2 b1 b0<br>
b0: Veto; b1: Loose; b2: Medium; b3: Tight and b4: HEEP<br>
To access the decision: <br>
   - Veto:   eleIDbit[]>>0&1 if 1--> this eID is passed<br>
   - Loose:  eleIDbit[]>>1&1<br>
   - Medium: eleIDbit[]>>2&1<br>
   - Tight:  eleIDbit[]>>3&1<br>
   - HEEP:   eleIDbit[]>>4&1<br>

Photons it is done the same way: it has 3 IDs, so 3 bits represent the decision<br>
To access the decision<br>
   - Loose:  phoIDbit[]>>0&1 if 1--> this phoID is passed<br>
   - Medium: phoIDbit[]>>1&1<br>
   - Tight:  phoIDbit[]>>2&1<br>

To access the MC status flag with GEN particles <br>
   - fromHardProcessFinalState : mcStatusFlag[]>>0&1 <br>
   - isPromptFinalState        : mcStatusFlag[]>>1&1 <br>
   - fromHardProcessBeforeFSR  : mcStatusFlag[]>>2&1 <br>

