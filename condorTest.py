#!/usr/bin/env python3
import os
import argparse
import sys
import ROOT

# Display the current directory:
print('Directory in which execution is done:')
print(os.getcwd())

# List files in the directory:
print('Files in the directory:')
for file in os.listdir(os.getcwd()):
    print('',file)

print('Total amount of  inputs:', len(sys.argv))
input_filename = sys.argv[0]
print( "The name of the file is ", input_filename)

arguments = {}

if len(sys.argv)>1:
    for argI in range(len(sys.argv)):
        print(argI, sys.argv[argI])
        if '=' in sys.argv[argI]:
            arguments[sys.argv[argI].split('=')[0]] = sys.argv[argI].split('=')[1]

print('Argument dictionary:')
print(arguments)

print(f'Date of submission: {sys.argv[3]}')
print(f'DSID: {sys.argv[4]}')

pathOnEOS = '/eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/MC23_SmallR_PFlow/MC23a/group.perf-jets.{dsid}.MC23aIJTR30v01_PFLOW_22112024_v01_tree.root'
pathOnEOS = pathOnEOS.format(dsid=sys.argv[4])
print(pathOnEOS)
if os.path.exists(pathOnEOS):
    print('File exists on EOS.')
else:
    print('File does not exist on EOS.')
        
# with open('condorTest.sub', 'w') as f:
    # f.write(templateCondorJob)

print('-'*38)
print('Display of: condor_stdout')
os.system('cat _condor_stdout')
print('-'*38)
print('Display of: condor_stderr')
os.system('cat _condor_stderr')
print('-'*38)
# print('Display of: job.ad')
# os.system('cat .job.ad')
# print('-'*38)
# print('Display of: machine.ad')
# os.system('cat .machine.ad')

rootFilePath= f'./ntuple_{sys.argv[4]}.tree.root'

if os.path.exists(rootFilePath):
    print('ROOT file exists.')
    f_in = ROOT.TFile.Open(rootFilePath,"read")
    ttree = f_in.Get('IsolatedJet_tree')
    print('Number of entris in a tree:',ttree.GetEntries())
    f_in.Close()
else:
    print('ROOT file does not exist:', rootFilePath)


if os.path.exists('./reweight.py'):
    print('Reweight script exists.')
else:
    print('Reweight script does not exist.')

command = f'python3 reweight.py --directory  {arguments["directory"]} --output {arguments["output"]}'

commandHelp = f'python3 reweight.py --help'

print(f'Help with the script:\n {commandHelp}')

os.system(commandHelp)

print(f'Command to execute:\n {command}')

os.system(command)

os.system('ls')
os.system('ls -lh')
