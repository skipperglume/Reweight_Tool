import ctypes
import os, sys
import argparse
from ROOT import *
import psutil
from configSettings import dsid, r_tag
def ERROR_print(text_string):
    print('ERROR: '+text_string+'.')
    exit(1)

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
        return

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
    def countDiskSpace(self):
        dirToIterate = []
        self.scores = []  
        for dir in [self.dirIn, self.dirOut]:
            if not dir == '':
                dirToIterate.append(dir)
        for dir in dirToIterate:
            print('------------------------------------')
            result = []
            fileDiskSpaceDict = {}
            result = self.getFilesRecursive(self.dirIn, result)
            tempScore = self.template
            for iter in result:

                eval = self.checkFile(iter)
                if eval == False:
                    continue
                if eval[1][-1].lower() in tempScore:
                    if eval[2] in tempScore[eval[1][-1].lower()]:
                        tempScore[eval[1][-1].lower()][eval[2]]['N'] += 1
                    else:
                        tempScore[eval[1][-1].lower()][eval[2]] = {}
                        tempScore[eval[1][-1].lower()][eval[2]]['N'] = 1
            print(tempScore)
            self.scores.append(tempScore)
            # print(len(result))
            print('------------------------------------')
        print(dirToIterate)
            # if self.useSpecifier:
                # if any(specifier in subDir for specifier in specificDirName):
                    # iterateDir = self.dirIn+'/'+subDir
                    # self.print_subDir(subDir, self.dirIn)
        #             onlyFiles = [f for f in os.listdir(iterateDir) if os.path.isfile(os.path.join(iterateDir, f))]
        #             print_files(onlyFiles, iterateDir)
        #             for f in onlyFiles:
        #                 if f[-5:] == '.root':
        #                     rootFiles.append(iterateDir+'/'+f )
                    
        #                 file_stats = os.stat(iterateDir+'/'+f)

        #                 for i in disk_space.keys():
        #                     if 'MC23'+i in iterateDir+'/'+f:
                                
        #                         disk_space[i] += file_stats.st_size/ 2.0**20
            
        #         for f in onlyFiles:
        #             if f[-5:] == '.root':
        #                 rootFiles.append(iterateDir+'/'+f )
                
        #             file_stats = os.stat(iterateDir+'/'+f)

        #             for i in disk_space.keys():
        #                 if 'MC23'+i in iterateDir+'/'+f:
                            
        #                     disk_space[i] += file_stats.st_size/ 2.0**20
            
                
                        
        
        # # print(rootFiles)
        # sizes = {'a':0, 'd':0, 'e':0,}

        # for j in rootFiles:
        #     for i in sizes.keys():
        #         if 'MC23'+i in j:
        #             sizes[i]+=1
        # print(sizes)
        # a = {}
        # lambda x : disk_space[x]/1024.0 , disk_space.keys()
        # for i in disk_space.keys():
        #     disk_space[i] = disk_space[i]/1024.
        # print(disk_space)
        # print(disk_space['a']+disk_space['d']+disk_space['e'])


        
        return 
if __name__ == "__main__":
    # Directories of root files: 
    directoryInput = '/eos/user/d/dtimoshy/MC23_CSSKUFO_7GeV/MC23c'
    directoryOutput = '/eos/user/d/dtimoshy/mc23_7GeV/MC23c/'

    specificDirName = ['group.perf-jets.801174.MC23aIJTR30v01_CSSKUFO_20230530_tree.root']
    # useSpecifier = True
    useSpecifier = False
    mc23cFilesTest = testOutput(directoryInput, directoryOutput, useSpecifier, specificDirName)
    mc23cFilesTest.countDiskSpace()
