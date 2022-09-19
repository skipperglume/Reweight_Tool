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

        parser = argparse.ArgumentParser(description='Reweight of multiple ntuples')
        parser.add_argument('-d','--directory', help="The directory of ntuples to be reweighted")
        parser.add_argument('-o','--output', help="The output directory")
        parser.add_argument('-t','--tree', default='IsolatedJet_tree', help="The ttree name")
        parser.add_argument('-H','--hist', default='MetaData_EventCount', help="Histogram containing cutflow")
        parser.add_argument('-w','--weight', default='sumw', help="Normalise by 'nevts' or 'sumw'")
        parser.add_argument('-n','--nevents', default=-1, type=int, help="The number of events to loop over (for all -1)")
        parser.add_argument('-b','--branch', default="weight", type=str, help="Branch of event's weight")
        opts = parser.parse_args()
        return opts
def print_files(arr,d):
    print("The directory: {} has files:".format(d) )
    for a in arr:
        print("  ",a)
def main():
    opts =  parse_options() 
    for i in r_tag:
        if i in opts.directory:
            R_TAG = i
    for i in dsid:
        if i in opts.directory:
            DSID = i
    if DSID=="" or R_TAG == "":
        print("ERROR in naming")
        return
    if (opts.output[-1] == "/"):
            opts.output = opts.output[:-1]    
    
    if (opts.directory[-1] == "/"):
            opts.directory = opts.directory[:-1]   

    onlyfiles = [f for f in os.listdir(opts.directory) if os.path.isfile(os.path.join(opts.directory, f))]
    print_files(onlyfiles, opts.directory)
    JZ_total_weight = 0
    
    
    for ttree_name in onlyfiles:
        fin = TFile.Open(opts.directory+'/'+ttree_name,"read")    
        ttree_f = fin.Get(opts.tree)
        
        if opts.hist!= '':
            thisto_f = fin.Get(opts.hist)
        
        nEntries = ttree_f.GetEntries()
        JZ_total_weight += thisto_f.GetBinContent(3)
        # print(thisto_f.GetBinContent(3))
        # for i in range(0, nEntries):
        #     ttree_f.GetEntry(i)
        #     JZ_total_weight+=ttree_f.weight  #*   len(ttree_f.jet_ConstitPt)
        
        
        fin.Close()
    print("Total reweight factor: ",JZ_total_weight)
    
    if not os.path.exists(opts.output):
        os.system("mkdir "+opts.output)
    opts.output = opts.output+"/"+R_TAG+"_"+DSID
    print("+I+",opts.output)
    if os.path.exists(opts.output):
            os.system("rm -rf "+opts.output)
    os.system("mkdir "+opts.output)
    print("\nFolder of rewweighted ntuples: ",opts.output)
    for file_name in onlyfiles:            
        fin = TFile.Open(opts.directory+"/"+file_name,"read")
        ttree_f = fin.Get(opts.tree)
        #t.Print()
        
        ttree_f.SetBranchStatus("*",1)
        ttree_f.SetBranchStatus("jet_ConstitE",0)
        
        if JZ_total_weight==0:
            print("ERROR: sumw==0")
            return 

        # Write ttree to new output file
        print("\n")
        
        
        #print("Creating output file : ",opts.output)
        path_to_output = opts.output+"/"+"__reweighted__"+file_name
        print(path_to_output)
        if os.path.exists(path_to_output):
            os.system("rm -rf "+path_to_output)
        fout = TFile(path_to_output,"recreate")


        Reweighted_ttree = ttree_f.CloneTree(0)
        
        Reweighted_ttree.SetBranchStatus("*",1)
        w = array('d',[-1])
        b = Reweighted_ttree.Branch("R_weight",w,"R_weight/D")
        #b.SetEntries(t.GetEntries())
        scale = array('d',[-1])
        b_scale = Reweighted_ttree.Branch("sumw",scale,"sumw/D")
        # Loop over events
        
        nEntries = ttree_f.GetEntries()

        for ievt in range(nEntries):
            ttree_f.GetEntry(ievt)
            
            w[0] = ttree_f.weight/JZ_total_weight
            scale[0] = JZ_total_weight
            Reweighted_ttree.Fill()
            

            

        # Reweighted_ttree.Write()
        
        fout.Close()
        
        print("OUTPUT "+path_to_output+ " is created")

        fin.Close()

    
    return 




if __name__ == "__main__":
    
    main()


    print("+I+")



# python3 reweight.py -d  /eos/user/d/dtimoshy/MC20_IJT/user.dtimoshy.364700.MC20a_364700_150922_tree.root  -o   /eos/user/d/dtimoshy/__RWED__MC20a
# python3 reweight.py -d  /eos/user/d/dtimoshy/MC20_IJT/user.dtimoshy.364708.MC20a_364708_150922_tree.root  -o   /eos/user/d/dtimoshy/__RWED__MC20a
# python3 reweight.py -d  /eos/user/d/dtimoshy/MC20_IJT/user.dtimoshy.364711.MC20a_364711_150922_tree.root  -o   /eos/user/d/dtimoshy/__RWED__MC20a
# python3 reweight.py -d  /eos/user/d/dtimoshy/MC20_IJT/user.dtimoshy.364712.MC20a_364712_150922_tree.root  -o   /eos/user/d/dtimoshy/__RWED__MC20a
# 14908796536.932829
'''
a = 1024
    address = id(a)
    print(address)
    print(ctypes.cast(address, ctypes.py_object).value)
'''