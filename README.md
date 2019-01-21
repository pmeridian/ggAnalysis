#### Current production tag : 
#### Newest tag for testing : 
#### This version can be run using CMSSW_9_4_10

##### To work with CMSSW_9_4_10:
cmsrel CMSSW_9_4_10 <br>
cd CMSSW_9_4_10/src <br>
cmsenv <br>
git cms-init <br>
git clone https://github.com/cmkuo/HiggsAnalysis.git <br>
git clone -b cmsdas2019 https://github.com/pmeridian/ggAnalysis.git <br>
git cms-merge-topic cms-egamma:EgammaPostRecoTools_940 <br>
git cms-merge-topic cms-egamma:EgammaID_949 <br>
git cms-merge-topic cms-met:METFixEE2017_949 <br>
scram b -j 8 <br>

Some informations on stored IDs.
eleID is stored in 64bit integer. Each bit represents the output of an ID selections<br>
for ELECRON ID stores 5 official 94x ID outputs: 5 IDs (Veto, Loose, Medium, Tight and HEEP) so only 5 bits are imp for us (59 bits of this integer  we are not using so may be we can change that to 16 bit integer later)<br>
Representing that integer in 5 bits: b4 b3 b2 b1 b0<br>
b0: Veto; b1: Loose; b2: Medium; b3: Tight and b4: HEEP<br>
To access the decision for <br>
(a) veto: eleIDbit[]>>0&1 ---> gives 0 or 1. if 0--> this eID is failed. if 1--> this eID is passed<br>
(b) Loose: eleIDbit[]>>1&1<br>
(c) Medium: eleIDbit[]>>2&1<br>
(d) Tight: eleIDbit[]>>3&1<br>
(e) HEEP: eleIDbit[]>>4&1<br>

for photons it is done the same way: it has 3 IDs<br>
so 3 bits represent the decision<br>
Representing that integer in 3 bits:  b2 b1 b0<br>
b0: Loose; b1: Medium; b2: Tight<br>
To access the decision for <br>
(a) Loose: phoIDbit[]>>0&1 ---> gives 0 or 1. if 0--> this phoID is failed. if 1--> this phoID is passed<br>
(b) Medium: phoIDbit[]>>1&1<br>
(c) Tight: phoIDbit[]>>2&1<br>

to access the MC status flag with GEN particles <br>
(a) fromHardProcessFinalState : mcStatusFlag[]>>0&1 ---> gives 0 (no) or 1 (yes). <br>
(b) isPromptFinalState        : mcStatusFlag[]>>1&1 ---> gives 0 (no) or 1 (yes). <br>
(c) fromHardProcessBeforeFSR  : mcStatusFlag[]>>2&1 ---> gives 0 (no) or 1 (yes). <br>

