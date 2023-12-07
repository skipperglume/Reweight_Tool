import ctypes
import os, sys
import argparse
from array import array
import ROOT
from configSettings import dsid, r_tag

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

def getEvntNum(inputTTree, inputHist):
    return inputTTree.GetEntries()
def getEvntWei(inputTTree, inputHist):
    return inputHist.GetBinContent(3)
def accumulateReweightFactor(onlyfiles, opts, outDict={'eventNumber':getEvntNum,'eventWeight':getEvntWei}, logPrint=True):
    result = 0 
    resultDict = {}
    for name in outDict.keys():
        resultDict[name] = 0 
    if logPrint:    print('start',resultDict)
    for file_name in onlyfiles:
        if (file_name[-5:] == ".part"):
            continue
        
        f_in = ROOT.TFile.Open(opts.directory+'/'+file_name,"read")    
        TTree_f = f_in.Get(opts.tree)
        
        
        
        if ( TTree_f != None and file_name[-6:-1] != ".part"):
            THisto_f = f_in.Get(opts.hist)
            result += THisto_f.GetBinContent(3)
            if logPrint: print(file_name, TTree_f.GetEntries(), THisto_f.GetBinContent(3))
            for var in outDict.keys():
                resultDict[var] += outDict[var](TTree_f, THisto_f)
        

        f_in.Close()
    if logPrint: print('end',resultDict)
    return (result, resultDict)
def Calculate_Reweight_Factor_Beam(onlyfiles, opts):
    result = 0 
    for file_name in onlyfiles:
        if (file_name[-5:] == ".part"):
            print("ERROR: zombie file")
            continue
        
        f_in = TFile.Open(opts.directory+'/'+file_name,"read")    
        TTree_f = f_in.Get(opts.tree)
        
        
        
        if ( TTree_f != None and file_name[-6:-1] != ".part"):
            print(file_name, TTree_f.GetEntries())
            nEntries = TTree_f.GetEntries()
            for ievt in range(nEntries):
                TTree_f.GetEntry(ievt)
                result += TTree_f.weight_beamSpotWeight
        print("Current total weight is: {0}".format(result))

        

        

        f_in.Close()
    return result
def Calculate_Reweight_Factor_mcEventWeight(onlyfiles, opts):
    result = 0 
    for file_name in onlyfiles:
        if (file_name[-5:] == ".part"):
            print("ERROR: zombie file")
            continue
        
        f_in = TFile.Open(opts.directory+'/'+file_name,"read")    
        TTree_f = f_in.Get(opts.tree)
        
        
        
        if ( TTree_f != None and file_name[-6:-1] != ".part"):
            print(file_name, TTree_f.GetEntries())
            nEntries = TTree_f.GetEntries()
            for ievt in range(nEntries):
                TTree_f.GetEntry(ievt)
                result += TTree_f.mcEventWeight
        print("Current total weight is: {0}".format(result))

        f_in.Close()
    return result

def Init_N_Clean(opts,R_TAG,DSID):
    if not os.path.exists(opts.output):
        os.system("mkdir "+opts.output)
    opts.output = opts.output+"/"+R_TAG+"_"+DSID
    
    if os.path.exists(opts.output):
            os.system("rm -rf "+opts.output)
    os.system("mkdir "+opts.output)
    print("\nFolder of reweighted ntuples: ",opts.output)
    return 

def main():
    R_TAG, DSID = "", ""
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
    # print_files(onlyfiles, opts.directory)
    
    reweightFactor,reweightDict =   accumulateReweightFactor(onlyfiles, opts, logPrint=False)
    print('rtag={}'.format(R_TAG),'dsid={}'.format(DSID),reweightFactor)
    print(reweightDict)
    exit(0)
    print("Total reweight factor: ",JZ_func)
    
    Init_N_Clean(opts,R_TAG,DSID)

    for file_name in onlyfiles:
        if (file_name[-5:] == ".part"):
            continue         

        fin = TFile.Open(opts.directory+"/"+file_name,"read")
        ttree_f = fin.Get(opts.tree)
        if ( ttree_f == None ):
            continue
        #t.Print()
        
        ttree_f.SetBranchStatus("*",1)
        ttree_f.SetBranchStatus("jet_ConstitE",0)
        ttree_f.SetBranchStatus("jet_Jvt",0)
        
        if JZ_func==0:
            print("ERROR: sumw==0")
            return 

        # Write ttree to new output file
        print("\n")
        
        
        #print("Creating output file : ",opts.output)
        path_to_output = opts.output+"/"+"__reweighted__"+file_name
        print(path_to_output)
        if os.path.exists(path_to_output):
            os.system("rm -rf "+path_to_output)
        
        fout = TFile(path_to_output,"create")
        Reweighted_ttree = ttree_f.CloneTree()

        
        
        Reweighted_ttree.SetBranchStatus("*",1)
        
        w = array('d',[-1])
        # w_pileUP_x_beamSpot = array('d',[-1])
        b = Reweighted_ttree.Branch("R_weight",w,"R_weight/D")
        # b_PUBSW = Reweighted_ttree.Branch("PU_BSW_weight",w_pileUP_x_beamSpot,"PU_BSW_weight/D")
        #b.SetEntries(t.GetEntries())
        scale = array('d',[-1])
        b_scale = Reweighted_ttree.Branch("sumw",scale,"sumw/D")
        # Loop over events
        
        nEntries = ttree_f.GetEntries()

        for ievt in range(nEntries):
            ttree_f.GetEntry(ievt)
            # If the weight is called "weight", then :
            # w[0] = ttree_f.weight/JZ_func
            # If the weight is called "weight_beamSpotWeight", then :
            # w[0] = ttree_f.weight_beamSpotWeight/JZ_func
            # If the weight is called "mcEventWeight", then :
            w[0] = ttree_f.weight/JZ_func
            scale[0] = JZ_func
            # w_pileUP_x_beamSpot[0] = ttree_f.weight_beamSpotWeight * ttree_f.weight_pileup
            # if ( ttree_f.weight_pileup != 1.0) :
                # print(ttree_f.weight_beamSpotWeight ,ttree_f.weight_pileup, w_pileUP_x_beamSpot)
            b.Fill()
            b_scale.Fill()
            # b_PUBSW.Fill()
            
        # Reweighted_ttree.Write()
        print("__reweighted__"+file_name,Reweighted_ttree.GetEntries())

        # Reweighted_ttree.Write()
        
        fin.Close()
        Reweighted_ttree.Write()
        fout.Close()
        
        print("OUTPUT "+path_to_output+ " is created")

        

    
    return 




if __name__ == "__main__":
    
    main()


    print("+I+")
    print("+I+")
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