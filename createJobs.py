import os
import re
import argparse
import sys
from datetime import datetime

'''
This script is used to create a list of commands to be run on the cluster via HTCondor.
The space pool is 20 GB per processing node.
Condor commands:
 - condor_submit JOB.sub
 - condor_q
 - condor_wait -status log/hello.70.log
'''


DSIDs = [
    # 801166,
    # 801167,
    # 801168,
    # 801169,
    # 801170,
    # 801171,
    # 801172,
    # 801173,
    801174,
]

templateCondorJob = '''
executable            = condorTest.py
arguments             = $(ClusterId) $(ProcId)
# input                 = input/mydata.$(ProcId)
output                = batch/output_condorTest.$(ClusterId).$(ProcId).out
error                 = batch/error_condorTest.$(ClusterId).$(ProcId).err
log                   = batch/log_condorTest.$(ClusterId).$(ProcId).log
+JobFlavour           = "espresso"
+MaxRuntime           = 10
queue
'''

templateCondorJobDated = '''
executable            = condorTest.py
arguments             = $(ClusterId) $(ProcId) {date} {dsid}
input                 = ntuple_801174.tree.root
output                = batch/output_{date}.$(ClusterId).$(ProcId).out
error                 = batch/error_{date}.$(ClusterId).$(ProcId).err
log                   = batch/log_{date}.$(ClusterId).$(ProcId).log
+JobFlavour           = "espresso"
+MaxRuntime           = 10
queue
'''
# input                 = reweight.py

templateCondorJobArgsDated = '''
executable            = condorTest.py
arguments             = $(ClusterId) $(ProcId) {date} {dsid} {directoryArg} {outputArg}
transfer_input_files  = reweight.py,configSettings.py,ntuple_801174.tree.root
output                = batch/output_{date}.$(ClusterId).$(ProcId).out
error                 = batch/error_{date}.$(ClusterId).$(ProcId).err
log                   = batch/log_{date}.$(ClusterId).$(ProcId).log
notification          = Always
notify_user           = "denys.timoshyn@cern.ch"
+JobFlavour           = "workday"
+MaxRuntime           = 10
queue
'''

def getDiskSpaceOfInput(pathToInput)->float:
    '''
    Get the disk space of the input file in GB.
    '''
    # print('-'*37)
    
    diskSpaceAccumulate = 0.0
    
    for root, dirs, files in os.walk(pathToInput):
        for fileIter in files:
            diskSpaceAccumulate += os.path.getsize(f'{root}/{fileIter}')
    
    # print('-'*37)
    
    diskSpaceAccumulate = round(diskSpaceAccumulate/1024/1024/1024, 1)
    
    print(pathToInput)
    # print(f'Disk space used: {diskSpaceAccumulate} GB')
    print(f'Disk space used: {diskSpaceAccumulate} GB')
    
    return diskSpaceAccumulate
    
def createCommand(dsidStr, addLogging=False):
    command = 'python3 reweight.py '
    
    pathToInput = f'/eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/MC23_SmallR_PFlow/MC23a/group.perf-jets.{dsidStr}.MC23aIJTR30v01_PFLOW_22112024_v01_tree.root'
    command += pathToInput + ' -d ' + pathToInput
    pathToOutput = '/eos/user/d/dtimoshy/MC23_PFlow/RW_test_MC23a'


    os.system(f'du {pathToInput} -sh')
    diskSpaceOfInput = getDiskSpaceOfInput(pathToInput)
    if diskSpaceOfInput > 20:
        print('Input file is too large for the cluster.')
        print(f'Disk space cut off is: 20 GB. Input disk space usage: {diskSpaceOfInput}.')
        return

    logFile = 'log_' + dsidStr + '.log'
    if addLogging:
        command += ' 2>&1 | tee log_' + str(dsid) + '.log'

    return command

    # commandPrefix = 
    # command
 
def condorTest(dsid, dryRun=True, pathToCondorSub='./condorSub/'):
    '''
    Writes temnplate to a file and submits it.
    '''
    # cleanBatch()
    
    dateSub = datetime.today().strftime('%d-%m-%Y')

    print(dateSub)
    pathToCondorSub += 'condorTest.sub'
    
    directoryArg = f'directory=/eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/MC23_SmallR_PFlow/MC23a/group.perf-jets.{dsid}.MC23aIJTR30v01_PFLOW_22112024_v01_tree.root'
    
    outputArg = 'output=/eos/user/d/dtimoshy/MC23_PFlow/condorMC23a'

    condorJob = templateCondorJobArgsDated
    condorJob = condorJob.format(date=dateSub, dsid=dsid, directoryArg=directoryArg, outputArg=outputArg)
    
    with open(pathToCondorSub, 'w') as f:
        f.write(condorJob)
    if dryRun:
        print(f'To execute run:\n  condor_submit {pathToCondorSub}')
    else:
        os.system(f'condor_submit {pathToCondorSub}')

def createCondorSubFile(dsid, dateSub, pathToCondorSub='./condorSub/'):
    return
    
def cleanBatch():
    '''
    Clean the batch directory.
    '''
    os.system('rm  batch/*')

def main(args:argparse.Namespace):
    '''
    Main function for producing a set of [.sub] files for condor to run.
    '''
    for dsid in DSIDs:
        print(dsid)
        condorTest(dsid)
    
    return
 
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Create a list of commands to be run on the cluster via HTCondor.')
    parser.add_argument('-s','--submit', action='store_true', help='Submit to condor.')
    
    args = parser.parse_args()
    
    # for dsid in DSIDs:
    #     print(dsid)
    #     print(createCommand(str(dsid)))
    # walkRecursively(os.getcwd())
    
    for dsid in DSIDs:
        print(dsid)
        condorTest(dsid, dryRun=(not args.submit))
        
    # Get number of standard arguments:
    exit(0)

# /pool/condor/dir_159793
    
    
# Error in <TNetXNGFile::Open>: [ERROR] Server responded with an error: [3010] Unable to open file __reweighted__group.perf-jets.42165003._000001.tree.root; Operation not permitted

# Error in <TNetXNGFile::Open>: [ERROR] Server responded with an error: [3010] Unable to open file __reweighted__group.perf-jets.42165003._000002.tree.root; Operation not permitted

# Error in <TNetXNGFile::Open>: [ERROR] Server responded with an error: [3010] Unable to open file __reweighted__group.perf-jets.42165003._000003.tree.root; Operation not permitted

# Getting r-tag and dsid for samples.
# Getting reweight factor.
# rtag=MC23a dsid=801174 1.886766155901495e-06
# {'eventNumber': 7221234, 'eventWeight': 1.886766155901495e-06, 'TotalWeight': 7.414092281343362e-10}
# Total reweight factor:  1.886766155901495e-06