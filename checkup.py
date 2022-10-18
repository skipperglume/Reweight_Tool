import ctypes
import os, sys
import argparse
from array import array
from ROOT import *
r_tag = ["MC20a","MC20d","MC20e"]

dsid = ["364700", "364701", "364702", "364703", "364704",
"364705", "364706", "364707", "364708", "364709", 
"364710", "364711", "364712"]
def parse_options():
        import argparse

        parser = argparse.ArgumentParser(description='Check that files are of proper format')
        parser.add_argument('-i','--input', help="The directory of ntuples to be checked on")
        
        parser.add_argument('-t','--tree', default='IsolatedJet_tree', help="The ttree name")
        parser.add_argument('-H','--hist', default='MetaData_EventCount', help="Histogram containing cutflow")
        
        
        
        opts = parser.parse_args()
        return opts
def print_files(arr,d):
    print("The directory: {} has files:".format(d) )
    for a in arr:
        print("  ",a)
def File_Is_Ok(onlyfiles, opts,error_array):
    
    for file_name in onlyfiles:
        if (file_name[-5:] == ".part" ):
            print(file_name, "ERROR: NON .root FILE")
            error_array.append(file_name+" NON .root FILE")
            continue
        
        f_in = TFile.Open(opts.input+'/'+file_name,"read")    
        TTree_f = f_in.Get(opts.tree)
        
        if ( TTree_f == None ):
            print(file_name, "ERROR: NO TTREE OBJECT")
            error_array.append(file_name +" NO TTREE OBJECT" )
            continue
        
        if ( TTree_f != None and file_name[-6:-1] != ".part"):
            # print(file_name, TTree_f.GetEntries())
            THisto_f = f_in.Get(opts.hist)
            

        

        

        

        f_in.Close()
    
    return
def main():
    R_TAG, DSID = "", ""
    opts =  parse_options() 
    for i in r_tag:
        if i in opts.input:
            R_TAG = i
    for i in dsid:
        if i in opts.input:
            DSID = i
    if DSID=="" or R_TAG == "":
        print("ERROR in naming")
        return

    if (opts.input[-1] == "/"):
            opts.input = opts.input[:-1]    

    if (opts.input[-1] == "/"):
            opts.input = opts.input[:-1]   
    onlyfiles = [f for f in os.listdir(opts.input) if os.path.isfile(os.path.join(opts.input, f))]
    # print_files(onlyfiles, opts.input)
    error_array =  [opts.input]
    File_Is_Ok(onlyfiles, opts,error_array)
    print(R_TAG, DSID)
    
    if(len(error_array)>1):
        print(error_array)
        print("ERRORS FOUND +I+")
if __name__ == "__main__":
    
    main()

    
    # print("+I+")
    # print("+I+")
    # print("+I+")

    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364700.MC20aIJTR22v01_091022_tree.root  

    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364700.MC20aIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364700.MC20dIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364700.MC20eIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364701.MC20aIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364701.MC20dIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364701.MC20eIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364702.MC20aIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364702.MC20dIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364702.MC20eIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364703.MC20aIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364703.MC20dIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364703.MC20eIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364704.MC20aIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364704.MC20dIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364704.MC20eIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364705.MC20aIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364705.MC20dIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364705.MC20eIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364706.MC20aIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364706.MC20dIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364706.MC20eIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364707.MC20aIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364707.MC20dIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364707.MC20eIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364708.MC20aIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364708.MC20dIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364708.MC20eIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364709.MC20aIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364709.MC20dIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364709.MC20eIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364710.MC20aIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364710.MC20dIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364710.MC20eIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364711.MC20aIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364711.MC20dIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364711.MC20eIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364712.MC20aIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364712.MC20dIJTR22v01_091022_tree.root
    #  python3 checkup.py -i /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.364712.MC20eIJTR22v01_091022_tree.root