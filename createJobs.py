import os
import re
import glob
import argparse
import sys
from datetime import datetime
from clean import removeDoubleSlashes, cleanBatch, cleanSubmissionFolder
'''
This script is used to create a list of commands to be run on the cluster via HTCondor.
The space pool is 20 GB per processing node.
Condor commands:
 - condor_submit JOB.sub
 - condor_q
 - condor_wait -status log/hello.70.log
'''

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
executable            = runJob.py
arguments             = $(ClusterId) $(ProcId) {JobIndex} {date} {dsid} {directoryArg} {outputArg}
transfer_input_files  = reweight.py,configSettings.py
output                = batch/output.{JobIndex}.out
error                 = batch/error.{JobIndex}.err
log                   = batch/log.{JobIndex}.log
# notification          = Always
# notify_user           = "denys.timoshyn@cern.ch"
+JobFlavour           = "workday"
queue
'''
# +MaxRuntime           = 10

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
        
def createCondorSubFile(jobParameters:dict, args:argparse.Namespace, pathToCondorSub='./condorSub/')->str:
    '''
    Method to create a condor sub file. Retrun the path to the sub file.
    Dictionary [jobParameters] should contain the following keys:
        - jobTemplate: The template for the condor job.
        - jobDate: Date of the job submission.
        - jobIter: The iteration of the job.
        - JobIndex: The index of the job.
        - dsid: The DSID of the job.
        - directoryArg: The directory of the input file.
        - outputArg: The directory of the output file.
        
    '''
    
    print('+++ Job Paramters +++')
    for param in jobParameters:
        print(f'{param}: {jobParameters[param]}')
    
    subFilePath = ''
    subFilePath = pathToCondorSub
    jobIter = jobParameters['jobIter']
    jobIndex = jobParameters['JobIndex']
    subFilePath += f'/condorReW_{jobIter}.sub'
    
    subFilePath = removeDoubleSlashes(subFilePath)
    
    condorJob = jobParameters['jobTemplate']
    
    condorJob = condorJob.format(date=jobParameters['jobDate'], 
                        dsid=jobParameters['dsid'], 
                        directoryArg=jobParameters['directoryArg'],     
                        outputArg=jobParameters['outputArg'],
                        JobIndex=jobParameters['JobIndex'],)
    
    print('+-'*19)

    with open(subFilePath, 'w') as f:
        f.write(condorJob)
        
    readeMePath = pathToCondorSub + f'/convert_{jobIndex}.readme'
    
    # Get string from dictionary:
    jobParametersStr = 'Job Parameters:\n'
    
    for param in jobParameters:
        jobParametersStr += f'{param}: {jobParameters[param]}\n'
        
    with open(readeMePath, 'w') as f:
        f.write(jobParametersStr)

    dryRun = not args.submit
    if dryRun:
        print(f'To execute run:\n  condor_submit {subFilePath}')
    else:
        os.system(f'condor_submit {subFilePath}')

    print('+-'*19)
    return subFilePath
    
def findNewJobIndex(pathToCondorSub='./condorSub/')->int:
    '''
    Find the next job index.
    '''

    jobIndex = 0

    while os.path.exists('{}/convert_{}.readme'.format(pathToCondorSub, jobIndex)):
        jobIndex += 1
    
    return jobIndex

def main(args:argparse.Namespace, submitDSID:list):
    '''
    Main function for producing a set of [.sub] files for condor to run.
    '''

    subFiles = []

    jobDate = datetime.today().strftime('%d-%m-%Y')

    for dsid in submitDSID:
        print(f'DSID: {dsid}')
        jobParameters = {}

        jobParameters['jobTemplate'] = templateCondorJobArgsDated

        jobParameters['jobDate'] = jobDate

        jobParameters['jobIter'] = submitDSID.index(dsid)
        jobParameters['JobIndex'] = findNewJobIndex()
        
        jobParameters['dsid'] = dsid
        # A value that is used to look up the directory of the input file.
        jobParameters['directoryArg'] = args.input_directory.format(dsid=dsid, campaign=args.campaign)
        foundFiles = glob.glob(jobParameters['directoryArg'])
        print(f'Found files: [{len(foundFiles)}]')

        if len(foundFiles) != 1 :
            print('Error: Found more than one file.')
            exit(0)
        else:
            print(f'File: {foundFiles[0]}')
            jobParameters['directoryArg'] = foundFiles[0]

        # /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/MC20_SmallR_PFlow/MC20a/group.perf-jets.*.Pythia8EvtGen_A14NNPDF23LO_jetjet_JZ*WithSW.MC20a_newIso_NeutShape_v01_120325_tree.root

        # A value that is used to look up the output directory.
        jobParameters['outputArg'] = args.output_directory.format(campaign=args.campaign)       
        subFiles += [createCondorSubFile(
            jobParameters=jobParameters,
            args=args,
        )]
        
    print(subFiles)
        
    for fileIter in range(len(subFiles)):
        print(f'[{fileIter+1}/{len(subFiles)}] : {subFiles[fileIter]}')
    
    return



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Create a list of commands to be run on the cluster via HTCondor.')
    parser.add_argument('-s','--submit', action='store_true', help='Submit to condor.')
    parser.add_argument('-clean','--clean', action='store_true', help='Clean the batch folder and folder containing the submission files.')
    parser.add_argument('-camp','--campaign', default='MC20a', help='NOT USED FOR NOW! Determines which campaign to run.')
    parser.add_argument('-dsids','--dsids', default='364700,364701,364702,364703,364704,364705,364706,364707,364708,364709,364710,364711,364712', help='Determines the list if DSID to run.')
    parser.add_argument('-id','--input_directory', default=r'/eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/MC20_SmallR_PFlow/{campaign}/group.perf-jets.{dsid}.Pythia8EvtGen_A14NNPDF23LO_jetjet_JZ*WithSW.MC20a_newIso_NeutShape_v01_120325_tree.root', type=str, help='Directory of the input files')
    parser.add_argument('-od','--output_directory', default=r'/eos/user/d/dtimoshy/MC23_PFlow/condor_{campaign}', type=str, help='Directory of the output files')
    args = parser.parse_args()
    
    if args.clean:
        cleanBatch()
        cleanSubmissionFolder()
        print('Cleaning complete.')
        exit(0)

    # Make sure all entries are unique:
    

    DSIDs = list(set(args.dsids.split(',')))
    main(args=args, submitDSID=DSIDs)
    
    # for dsid in DSIDs:
    #     print(dsid)
    #     print(createCommand(str(dsid)))
    # walkRecursively(os.getcwd())
    
    # for dsid in DSIDs:
        # print(dsid)
        # condorTest(dsid, dryRun=(not args.submit))
        
    # Get number of standard arguments:
    exit(0)

# /pool/condor/dir_159793
