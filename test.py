import ctypes
import os, sys
import argparse
from array import array
from ROOT import *
import psutil
def ERROR_print(text_string):
    print('ERROR: '+text_string+'.')
    exit(1)

class testOutout:
    def __init__(self, directoryInput, directoryOutput='', useSpecifier=False, specificDirName=[]):
        self.dirIn = directoryInput
        self.dirOut = directoryOutput
        self.disk_space = {'a':0, 'd':0, 'e':0,}
        self.rootFiles = []
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
                    print('appended')
                    # print(result)

        return result



    def checkFile(self, fileName, extension='.root', suffix='', midSubstring=[]):
        result = []
        if os.path.isdir(dir):
            ERROR_print('{0} is a directory')
        if os.path.isfile(f):
            if not f[-len(extension):] == extension:
                return False
            if not f[:len(suffix)] == suffix:
                return False
            for substring in midSubstring:
                if not substring in fileName:
                    return False
        return True

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
        onlySubDirs = [f for f in os.listdir(self.dirIn) if os.path.isdir(os.path.join(self.dirIn, f))]
        result = []
        result = self.getFilesRecursive(self.dirIn, result)
        # result = [x  for x in result if self.checkFile(x)]
        print('------------------------------------')
        for rootFile in result:
            print(rootFile)
        print('------------------------------------')
        print(len(result))
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
    # Directory of ntuple root files: 
    
    # directory = '/eos/user/d/dtimoshy/MC23_CSSKUFO_7GeV/MC23c'
    # directory = '/eos/user/d/dtimoshy/mc23_7GeV/MC23c/user.dtimoshy.801174.MC23cIJTR30v01_CSSKUFO_221123_tree.root'
    directoryInput = '/eos/user/d/dtimoshy/MC23_CSSKUFO_7GeV/MC23c'
    directoryOutput = '/eos/user/d/dtimoshy/mc23_7GeV/MC23c/user.dtimoshy.801174.MC23cIJTR30v01_CSSKUFO_221123_tree.root'

    specificDirName = ['group.perf-jets.801174.MC23aIJTR30v01_CSSKUFO_20230530_tree.root']
    # useSpecifier = True
    useSpecifier = False
    mc23cFilesTest = testOutout(directoryInput, directoryOutput, useSpecifier, specificDirName)
    mc23cFilesTest.countDiskSpace()
