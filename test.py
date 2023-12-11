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
    return x / (1024 ** 3)


def getNumberOfEvents(path):
    print(path)
    return 10
def getEventWeight(path):
    return 3.3
class testOutput:

    template = {'c':{}}

    def __init__(self, directoryInput, directoryOutput='', useSpecifier=False, specificDirName=[]):
        self.dirIn = directoryInput
        self.dirOut = directoryOutput
        self.disk_space = {'a':0, 'd':0, 'e':0,}
        self.rootFiles = []
        self.scores = []  
        self.specificDirName = specificDirName
        self.useSpecifier = useSpecifier
        self.dirToIterate = []
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
        print('INFO')
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
    def fillVariable(self, name, funcInit='', funcAccum='')->None:
        
        for dir in [self.dirIn, self.dirOut]:
            if dir:
                self.dirToIterate.append(dir)
        for dir in self.dirToIterate:
            result = []
            result = self.getFilesRecursive(dir, result)
            tempScore = copy.deepcopy(self.template)
            for iter in result:
                eval = self.checkFile(iter)
                if not eval :
                    continue
                if eval[1][-1].lower() in tempScore:
                    if eval[2] in tempScore[eval[1][-1].lower()]:
                        tempScore[eval[1][-1].lower()][eval[2]][name] += funcAccum(iter)
                    else:
                        tempScore[eval[1][-1].lower()][eval[2]][name] = funcInit(iter)
            self.scores.append(tempScore)
        return None
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
                        # tempScore[eval[1][-1].lower()][eval[2]]['N'] += 1
                        # tempScore[eval[1][-1].lower()][eval[2]]['DiskSpace'] += os.path.getsize(iter)
                    else:
                        tempScore[eval[1][-1].lower()][eval[2]] = {'paths':[iter]}
                        # tempScore[eval[1][-1].lower()][eval[2]] = {'N':1, 'DiskSpace':os.path.getsize(iter), 'path':iter}
                else:
                    pass
            print(tempScore)
            self.scores.append(tempScore)
            print('------------------------------------')
        print(self.dirToIterate)
        return 


        
if __name__ == "__main__":
    # Directories of root files: 
    directoryInput = '/eos/user/d/dtimoshy/mc23_7GeV/MC23c/'
    directoryOutput = '/eos/user/d/dtimoshy/MC23_CSSKUFO_7GeV/MC23c'

    # directoryInput = '/eos/user/d/dtimoshy/mc23/MC23c/'
    # directoryOutput = '/eos/user/d/dtimoshy/MC23_CSSKUFO/MC23c'

    specificDirName = ['group.perf-jets.801174.MC23aIJTR30v01_CSSKUFO_20230530_tree.root']
    # useSpecifier = True
    useSpecifier = False
    mc23cFilesTest = testOutput(directoryInput, directoryOutput, useSpecifier, specificDirName)
    mc23cFilesTest.fillFilePath()
    
    print('++++++++++++++++++++++++++++++')
    # print(mc23cFilesTest.getTotalSum(func=returnX))
    # print(mc23cFilesTest.getTotalSum(name='DiskSpace',func=returnGB))
    mc23cFilesTest.diplayInfo('paths', len)
    # mc23cFilesTest.diplayInfo(name='DiskSpace',func=returnGB)
