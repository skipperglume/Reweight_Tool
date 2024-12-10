import ROOT
import ctypes
import argparse
import os, sys
import psutil
from configSettings import dsid, r_tag, ERROR_print
import copy

def returnOne(x):
    return 1

def returnX(x):
    return x

def returnGB(x):
    return  "{:0.1f} GB".format(round(x / (1024 ** 3)))

def getNumberOfEvents(path)->int:
    result = 0
    file = ROOT.TFile.Open(path, 'read')
    tree = file.Get('IsolatedJet_tree')
    result = tree.GetEntries()
    file.Close()
    return result

def getEventWeight(path)->float:
    result = 0
    file = ROOT.TFile.Open(path, 'read')
    tree = file.Get('IsolatedJet_tree')
    tree.SetBranchStatus("*",0)
    tree.SetBranchStatus("weight",1)
    nEntries = tree.GetEntries()
    for ievt in range(nEntries):
        tree.GetEntry(ievt)
        result += tree.weight
    file.Close()
    return result

def getEventReWeight(path)->float:
    result = 0
    file = ROOT.TFile.Open(path, 'read')
    tree = file.Get('IsolatedJet_tree')
    tree.SetBranchStatus("*",0)
    tree.SetBranchStatus("R_weight",1)
    nEntries = tree.GetEntries()
    for ievt in range(nEntries):
        tree.GetEntry(ievt)
        result += tree.R_weight
    file.Close()
    return result

def listTTree(path):
    result = 0
    file = ROOT.TFile.Open(path, 'read')
    tree = file.Get('IsolatedJet_tree')
    tree.SetBranchStatus("*",0)
    tree.Print()
    file.Close()
    exit(0)
    return result

def getJetsNumber(path)->int:
    result = 0
    file = ROOT.TFile.Open(path, 'read')
    tree = file.Get('IsolatedJet_tree')
    tree.SetBranchStatus("*",0)
    tree.SetBranchStatus("jet_pt",1)
    vec = ROOT.std.vector('float')()
    tree.SetBranchAddress("jet_pt", vec)
    nEntries = tree.GetEntries()
    for ievt in range(nEntries):
        tree.GetEntry(ievt)
        result += vec.size()
    file.Close()
    return result

class testOutput:

    template = {'a' : {},'c' : {}, 'd': {}}

    def __init__(self, directoryInput, directoryOutput='', useSpecifier=False, specificDirName=[]):
        self.dirIn = directoryInput
        self.dirOut = directoryOutput
        self.disk_space = {'a':0, 'd':0, 'e':0,}
        self.rootFiles = []
        self.scores = []  
        self.specificDirName = specificDirName
        self.useSpecifier = useSpecifier
        self.dirToIterate = []
        self.listOfVariablesNames=set()
        return

    def getTotalSum(self, name='N', func=None):
        result = []
        for score in self.scores:
            currentIter = {}
            for key in score.keys():
                for dsid in score[key].keys():
                    if name in score[key][dsid].keys():
                        if key in currentIter.keys():
                            if func==None:
                                currentIter[key] += 1
                            else:
                                currentIter[key] += func(score[key][dsid][name])
                        else:
                            if func==None:
                                currentIter[key] = 1
                            else:
                                currentIter[key] = func(score[key][dsid][name])
            result.append(currentIter)
        return result

    def getFilesRecursive(self, dir, result):
        if os.path.isdir(dir):
            for f in os.listdir(dir):
                newPath = dir+'/'+f
                # print('newPath: '+newPath)
                if os.path.isdir(newPath):
                    # print('recursive '+newPath)
                    self.getFilesRecursive(newPath, result)
                if os.path.isfile(newPath):
                    result.append(newPath)

        return result

    def checkFile(self, fileName, extension='.root', suffix='', midSubstring=[]):
        result = []
        if os.path.isdir(fileName):
            ERROR_print('{0} is a directory')
        if os.path.isfile(fileName):
            if not fileName[-len(extension):] == extension:
                return False
            if not fileName[:len(suffix)] == suffix:
                return False
            for substring in midSubstring:
                if not substring in fileName:
                    return False
        foundDSID = ''
        for DSID in dsid:
            if DSID in fileName:
                foundDSID = DSID
                break
        foundRTAG = ''
        for RTAG in r_tag:
            if RTAG.upper() in fileName.upper():
                foundRTAG = RTAG
                break
        return (0, foundRTAG, foundDSID)

    def print_files(self, arr,d):
        print("The directory: {} has files:".format(d) )
        for a in arr:
            print("    {}".format(a))
        return

    def print_subDir(self, arr,d):
        print("The directory: {} has subdir:".format(d) )
        print("  {}".format(arr))
        return

    def diplayInfo(self, name='N', func=returnX)->None:
        print('INFO on {0}'.format(name))
        for iter in range(len(self.scores)):
            score = self.scores[iter]
            path = self.dirToIterate[iter]
            if self.dirIn == path:
                print('Input',path)
            elif self.dirOut == path:
                print('Output',path)
            else:
                print(path)
            for rtag in score.keys():
                print(rtag)
                for dsid in score[rtag].keys():
                    print('  ', dsid)
                    if not name in score[rtag][dsid].keys() :
                        ERROR_print('variable {0} is not present in keys {1}'.format(name, score[rtag][dsid].keys()))
                    print('   ',func(score[rtag][dsid][name]))
        return None

    def diplayDiff(self, name='N', func=returnX)->None:
        print('DIFF INFO')
        if not len(self.scores) == 2:
            ERROR_print('incorrect size')

        for iter in range(len(self.scores)):
            score = self.scores[iter]
            path = self.dirToIterate[iter]
            if self.dirIn == path:
                print('Input',path)
            elif self.dirOut == path:
                print('Output',path)
            else:
                print(path)
            for rtag in score.keys():
                print(rtag)
                for dsid in score[rtag].keys():
                    print('  ', dsid)
                    if not name in score[rtag][dsid].keys() :
                        ERROR_print('variable {0} is not present in keys {1}'.format(name, score[rtag][dsid].keys()))
                    print('   ',func(score[rtag][dsid][name]))
        return None
    def listVariableName(self)->None:
        for i_Name in self.listOfVariablesNames:
            print(i_Name)
        return
    def fillVariable(self, name, funcInit=None, funcAccum=None)->None:
        
        print('Started variable {0}'.format(name))
        for score in self.scores:
            for campaign in score.keys():
                for dsid in score[campaign].keys():
                    for path in score[campaign][dsid]['paths']:
                        if not name in score[campaign][dsid]:
                            if funcInit:
                                score[campaign][dsid][name] = funcInit(path)
                                self.listOfVariablesNames.add(name)
                        else:
                            if funcAccum:
                                score[campaign][dsid][name] += funcAccum(path)
                        
        print('Finished with variable {0}'.format(name))
        return None
    def saveToPickle(self)->None:
        import pickle
        
        return
    def fillFilePath(self):
        self.dirToIterate = []
        self.scores = []  
        for dir in [self.dirIn, self.dirOut]:
            if dir:
                self.dirToIterate.append(dir)
        for dir in self.dirToIterate:
            print('------------------------------------')
            result = []
            result = self.getFilesRecursive(dir, result)
            tempScore = copy.deepcopy(self.template)
            for iter in result:
                eval = self.checkFile(iter)
                if not eval :
                    continue
                if eval[1][-1].lower() in tempScore:
                    if eval[2] in tempScore[eval[1][-1].lower()]:
                        tempScore[eval[1][-1].lower()][eval[2]]['paths'] += [iter]
                    else:
                        tempScore[eval[1][-1].lower()][eval[2]] = {'paths':[iter]}
            self.scores.append(tempScore)
            print('------------------------------------')
        print(self.dirToIterate)
        return 

if __name__ == "__main__":
    '''
    This code tests that the new reweighted files are in a proper structure: same amount of events, same amount of files. 
    Check the resulting disk spaces.
    '''
    # Directories of root files: 
    # directoryInput = '/eos/user/d/dtimoshy/mc23_7GeV/MC23c/'
    # directoryOutput = '/eos/user/d/dtimoshy/MC23_CSSKUFO_7GeV/'
    directoryOutput = '/eos/user/d/dtimoshy/MC23_PFlow/MC23a/'

    # directoryInput = '/eos/user/d/dtimoshy/mc23/MC23c/'
    # directoryInput  = '/eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/MC23_SmallR_UFO_7GeV/'
    directoryInput  = '/eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/MC23_SmallR_PFlow/MC23a/'

    specificDirName = ['group.perf-jets.801174.MC23aIJTR30v01_CSSKUFO_20230530_tree.root']
    # useSpecifier = True
    useSpecifier = False
    mc23cFilesTest = testOutput(directoryInput, directoryOutput, useSpecifier, specificDirName)
    mc23cFilesTest.fillFilePath()
    mc23cFilesTest.fillVariable(name='Nfiles', funcInit=returnOne, funcAccum=returnOne)
    mc23cFilesTest.fillVariable(name='DiskSize', funcInit=os.path.getsize, funcAccum=os.path.getsize)
    mc23cFilesTest.fillVariable(name='Entries', funcInit=getNumberOfEvents, funcAccum=getNumberOfEvents)
    # mc23cFilesTest.fillVariable(name='EventWeight', funcInit=getEventWeight, funcAccum=getEventWeight)
    # mc23cFilesTest.fillVariable(name='EventReWeight', funcInit=getEventReWeight, funcAccum=getEventReWeight)
    # mc23cFilesTest.fillVariable(name='Njets', funcInit=getJetsNumber, funcAccum=getJetsNumber)
    
    # print('++++++++++++++++++++++++++++++')
    # mc23cFilesTest.fillVariable(name='None', funcInit=listTTree, funcAccum=None)

    print('++++++++++++++++++++++++++++++')
    mc23cFilesTest.listVariableName()
    # print(mc23cFilesTest.getTotalSum(func=returnX))
    # print(mc23cFilesTest.getTotalSum(name='DiskSpace',func=returnGB))
    mc23cFilesTest.diplayInfo('paths', returnOne)
    mc23cFilesTest.diplayInfo('Nfiles')
    mc23cFilesTest.diplayInfo('DiskSize', returnGB)
    mc23cFilesTest.diplayInfo('Entries')
    # mc23cFilesTest.diplayInfo('EventWeight')
    # mc23cFilesTest.diplayInfo('EventReWeight')
    # mc23cFilesTest.diplayInfo('Njets')

    # import pickle
    # filehandler = open('saveObject.pickle', 'rb') 
    # from test import testOutput
    # object = pickle.load(filehandler)