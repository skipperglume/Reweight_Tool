import ctypes
import os, sys
import argparse
from array import array
from ROOT import *
import psutil

def print_files(arr,d):
    print("The directory: {} has files:".format(d) )
    for a in arr:
        print("    {}".format(a))
def print_subDir(arr,d):
    print("The directory: {} has subdir:".format(d) )
    print("  {}".format(arr))
if __name__ == "__main__":
    rootFiles = []
    # Directory of ntuple root files: 
    # directory = '/eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib_UFO_BeamSpot/'
    # directory = '/eos/user/d/dtimoshy/MC20_Beam_weight/MC20d'
    
    # directory = '/eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/PFlow_MC23a'
    # directory = '/eos/user/d/dtimoshy/MC23_PFlow/MC23a'
    
    # directory = '/eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/CSSKUFO_MC23a/'
    directory = '/eos/user/d/dtimoshy/MC23_CSSKUFO/MC23a'

    specificDirName = ['group.perf-jets.801174.MC23aIJTR30v01_CSSKUFO_20230530_tree.root']
    # useSpecifier = True
    useSpecifier = False
    
    disk_space = {'a':0, 'd':0, 'e':0,}
    onlySubDirs = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
    for subDir in onlySubDirs:
        if useSpecifier:
            if any(specifier in subDir for specifier in specificDirName):
                iterateDir = directory+'/'+subDir
                print_subDir(subDir, directory)
                onlyFiles = [f for f in os.listdir(iterateDir) if os.path.isfile(os.path.join(iterateDir, f))]
                print_files(onlyFiles, iterateDir)
                for f in onlyFiles:
                    if f[-5:] == '.root':
                        rootFiles.append(iterateDir+'/'+f )
                
                    file_stats = os.stat(iterateDir+'/'+f)

                    for i in disk_space.keys():
                        if 'MC23'+i in iterateDir+'/'+f:
                            
                            disk_space[i] += file_stats.st_size/ 2.0**20
        else : 
            iterateDir = directory+'/'+subDir
            print_subDir(subDir, directory)
            onlyFiles = [f for f in os.listdir(iterateDir) if os.path.isfile(os.path.join(iterateDir, f))]
            print_files(onlyFiles, iterateDir)
            for f in onlyFiles:
                if f[-5:] == '.root':
                    rootFiles.append(iterateDir+'/'+f )
            
                file_stats = os.stat(iterateDir+'/'+f)

                for i in disk_space.keys():
                    if 'MC23'+i in iterateDir+'/'+f:
                        
                        disk_space[i] += file_stats.st_size/ 2.0**20
        
            
                    
    
    # print(rootFiles)
    sizes = {'a':0, 'd':0, 'e':0,}

    for j in rootFiles:
        for i in sizes.keys():
            if 'MC23'+i in j:
                sizes[i]+=1
    print(sizes)
    a = {}
    lambda x : disk_space[x]/1024.0 , disk_space.keys()
    for i in disk_space.keys():
        disk_space[i] = disk_space[i]/1024.
    print(disk_space)
    print(disk_space['a']+disk_space['d']+disk_space['e'])



# {'a': 201, 'e': 0, 'd': 0}
# 137.262482474
# 8.780163052118581
# {'a': 0, 'e': 0, 'd': 134}
# 111.861917418
# 7.571255368608334
# {'a': 0, 'e': 431, 'd': 0}
# 203.220876507
# 14.870787676884845
# {'a': 201, 'e': 431, 'd': 134}
# 483.567482497

{'a': 146.04264552611858, 'e': 218.09166418388486, 'd': 119.43317278660834}
# /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/CSSKUFO_MC23a//group.perf-jets.801174.MC23aIJTR30v01_CSSKUFO_20230530_tree.root/group.perf-jets.33881406._000007.tree.root - 197586

# /eos/user/d/dtimoshy/MC23_CSSKUFO/MC23a/MC23a_801174/__reweighted__group.perf-jets.33881406._000007.tree.root - 197586
# 33.0276242793 - 31.0333749224 = 1.9942493568999993
# 53.4216510383 - 49.956381049 = 3.4652699892999976