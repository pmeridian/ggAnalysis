import subprocess
import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing('analysis')
options.register('datasets',
                 '',
                 VarParsing.multiplicity.list,
                 VarParsing.varType.string,
                 "Input dataset(s)")
options.register('output',
                 '',
                 VarParsing.multiplicity.singleton,
                 VarParsing.varType.string,
                 "output file name")
options.maxEvents = -1
options.parseArguments()

files = []
files2 = []
for dataset in options.datasets:
    print('>> Creating list of files from: \n'+dataset)
    query = "-query='file dataset="+dataset+"'"
    if options.debug:
        print(query)
    lsCmd = subprocess.Popen(['dasgoclient '+query+' -limit=0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    str_files, err = lsCmd.communicate()
    files.extend(['root://cms-xrd-global.cern.ch/'+ifile for ifile in str_files.split("\n")])
    files = [k for k in files if options.pattern in k]
    files.pop()

process = cms.Process('ggKit')

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.options = cms.untracked.PSet( allowUnscheduled = cms.untracked.bool(True) )

process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff" )
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
if (not isMC):
    process.GlobalTag = GlobalTag(process.GlobalTag, '94X_dataRun2_ReReco_EOY17_v6')
else:
    process.GlobalTag = GlobalTag(process.GlobalTag, '94X_mc2017_realistic_v14')

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1000) )
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.source = cms.Source(
    "PoolSource",
    fileNames = cms.untracked.vstring(files)
    )
process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')

#process.load("PhysicsTools.PatAlgos.patSequences_cff")

process.load( "PhysicsTools.PatAlgos.producersLayer1.patCandidates_cff" )
if (not isMC):
    process.load( "PhysicsTools.PatAlgos.triggerLayer1.triggerProducer_cff" )
process.load( "PhysicsTools.PatAlgos.selectionLayer1.selectedPatCandidates_cff" )

### fix a bug in the ECAL-Tracker momentum combination when applying the scale and smearing
from RecoEgamma.EgammaTools.EgammaPostRecoTools import setupEgammaPostRecoSeq
setupEgammaPostRecoSeq(process,
                       runVID=False,
                       era='2017-Nov17ReReco') 

#from PhysicsTools.PatAlgos.tools.cmsswVersionTools import *
from PhysicsTools.PatAlgos.tools.coreTools import *
if (not isMC):
    runOnData( process,  names=['Photons', 'Electrons','Muons','Taus','Jets'], outputModules = [] )
#runOnData( process, outputModules = [] )
#removeMCMatching(process, names=['All'], outputModules=[])

process.TFileService = cms.Service(
    "TFileService",
    fileName = cms.string(options.output)
    )

### reduce effect of high eta EE noise on the PF MET measurement (to be changed in 2017 re-reco)
from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
if (not isMC):
    runMetCorAndUncFromMiniAOD (
        process,
        isData = True, 
        fixEE2017 = True,
        postfix = "ModifiedMET"
        )
else:
    runMetCorAndUncFromMiniAOD(process,
                               isData=False
                               )

process.load("ggAnalysis.ggNtuplizer.ggNtuplizer_miniAOD_cfi")
process.ggNtuplizer.year=cms.int32(2017)
if (not isMC):
    process.ggNtuplizer.doGenParticles=cms.bool(False)
else:
    process.ggNtuplizer.doGenParticles=cms.bool(True)
process.ggNtuplizer.dumpPFPhotons=cms.bool(False)
process.ggNtuplizer.dumpHFElectrons=cms.bool(False)
process.ggNtuplizer.dumpJets=cms.bool(True)
process.ggNtuplizer.dumpAK8Jets=cms.bool(False)
process.ggNtuplizer.dumpSoftDrop= cms.bool(True)
process.ggNtuplizer.dumpTaus=cms.bool(False)
if (not isMC):
    process.ggNtuplizer.pfMETLabel=cms.InputTag("slimmedMETsModifiedMET")
else:
    process.ggNtuplizer.triggerEvent=cms.InputTag("slimmedPatTrigger", "", "PAT")

if (not isMC):
    process.p = cms.Path(
        process.fullPatMetSequenceModifiedMET *
        process.ggNtuplizer
        )
else:
    process.p = cms.Path(
        process.ggNtuplizer
        )

#print process.dumpPython()
