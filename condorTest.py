#!/usr/bin/env python3
import os
import argparse
import sys

print('Directory in which execution is done:')
print(os.getcwd())

print('Total amount of  inputs:', len(sys.argv))
input_filename = sys.argv[0]
print( "The name of the file is ", input_filename)

if len(sys.argv)>1:
    for argI in range(len(sys.argv)):
        print(argI,sys.argv[argI])
        
        
# with open('condorTest.sub', 'w') as f:
    # f.write(templateCondorJob)