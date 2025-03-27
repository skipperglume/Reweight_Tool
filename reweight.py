import ctypes
import os, sys
import argparse
from array import array
import ROOT
from configSettings import dsid, r_tag, ERROR_print

def parseOptions()->dict:
    '''
    Parse the command line options and return a dictionary of options
    '''
    parser = argparse.ArgumentParser(description='Reweight of multiple ntuples')
    parser.add_argument('-d','--directory', help="The directory of ntuples to be reweighted")
    parser.add_argument('-o','--output', help="The output directory")
    parser.add_argument('-t','--tree', default='IsolatedJet_tree', help="The ttree name")
    parser.add_argument('-H','--hist', default='MetaData_EventCount', help="Histogram containing cutflow")
    parser.add_argument('-w','--weight', default='sumw', help="Normalise by 'nevts' or 'sumw'")
    parser.add_argument('-b','--branch', default="weight", type=str, help="Branch of event's weight")
    args = parser.parse_args()
    return args

def print_files(arr,d):
    print("The directory: {} has files:".format(d) )
    for a in arr:
        print("  ",a)

def getEvntNum(inputTTree, inputHist):
    return inputTTree.GetEntries()

def getEvntWei(inputTTree, inputHist):
    return inputHist.GetBinContent(3)

def getTotWe(inputTTree, inputHist):
    result = 0 
    inputTTree.SetBranchStatus("*",0)
    inputTTree.SetBranchStatus("weight",1)

    nEntries = inputTTree.GetEntries()
    for ievt in range(nEntries):
        inputTTree.GetEntry(ievt)
        result += inputTTree.weight
    inputTTree.SetBranchStatus("*",1)
    return result

def getTotRWe(inputTTree, inputHist):
    result = 0 
    inputTTree.SetBranchStatus("*",0)
    inputTTree.SetBranchStatus("R_weight",1)

    nEntries = inputTTree.GetEntries()
    for ievt in range(nEntries):
        inputTTree.GetEntry(ievt)
        result += inputTTree.R_weight

    inputTTree.SetBranchStatus("*",1)
    return result
    # result += TTree_f.weight_beamSpotWeight
    # result += TTree_f.mcEventWeight

def accumulateReweightFactor(onlyfiles, dir, opts, outDict={'eventNumber':getEvntNum,'eventWeight':getEvntWei}, logPrint=True):
    result = 0 
    resultDict = {}
    for name in outDict.keys():
        resultDict[name] = 0 
    if logPrint:    print('start',resultDict)
    for file_name in onlyfiles:
        if (file_name[-5:] == ".part"):
            continue
        
        f_in = ROOT.TFile.Open(dir+'/'+file_name,"read")    
        TTree_f = f_in.Get(opts.tree)
        
        if ( TTree_f != None and file_name[-6:-1] != ".part"):
            THisto_f = f_in.Get(opts.hist)
            if THisto_f:
                result += THisto_f.GetBinContent(3)
            if logPrint: print(file_name, TTree_f.GetEntries(), THisto_f.GetBinContent(3))
            for var in outDict.keys():
                resultDict[var] += outDict[var](TTree_f, THisto_f)
        
        f_in.Close()
    if logPrint: print('end',resultDict)
    return (result, resultDict)

def Init_N_Clean(opts,R_TAG,DSID):
    if not os.path.exists(opts.output):
        os.system("mkdir "+opts.output)
    opts.output = opts.output+"/"+R_TAG+"_"+DSID
    
    if os.path.exists(opts.output):
            os.system("rm -rf "+opts.output)
    os.system("mkdir "+opts.output)
    print("\nFolder of reweighted ntuples: ",opts.output)
    return 

def createCopyJZ(onlyfiles, opts, fileIter = -1):

    for file_name in onlyfiles:
        if (file_name[-5:] == ".part"):
            ERROR_print('file is not finished: {0}'.format(file_name))
        if fileIter >= 0:
            if not onlyfiles[fileIter] == file_name:
                continue
            
        fin = ROOT.TFile.Open(opts.directory+"/"+file_name,"read")
        ttree_f = fin.Get(opts.tree)
        if ( ttree_f == None ):
            ERROR_print('ttree is None')
        
        ttree_f.SetBranchStatus("*",1)
        ttree_f.SetBranchStatus("jet_ConstitE",0)
        ttree_f.SetBranchStatus("jet_Jvt",0)
        
        # Write ttree to new output file
        path_to_output = opts.output+"/"+"__reweighted__"+file_name
        print("Creating output file :", path_to_output)
        if os.path.exists(path_to_output):
            os.system("rm -rf "+path_to_output)
        
        fout = ROOT.TFile(path_to_output,"create")
        fout.cd()
        Reweighted_ttree = ttree_f.CloneTree()
        fin.Close()
        Reweighted_ttree.Write()
        fout.Close()
    return

def addReweightBranch(onlyfilesOut, opts, reweightFactor=0, fileIter=-1):
    for file_name in onlyfilesOut:
        if fileIter >= 0:
            if not onlyfilesOut[fileIter] == file_name:
                continue
        path_to_output = opts.output+"/"+"__reweighted__"+file_name
        print('Adding new branch to:',path_to_output)
        fout = ROOT.TFile.Open(path_to_output,"update")
        ttree = fout.Get(opts.tree)

        ttree.SetBranchStatus("*",1)
        ttree.SetBranchStatus("weight",1)
        w = array('d',[-1])
        b = ttree.Branch("R_weight",w,"R_weight/D")
        scale = array('d',[-1])
        b_scale = ttree.Branch("sumw",scale,"sumw/D")
        
        nEntries = ttree.GetEntries()

        for ievt in range(nEntries):
            ttree.GetEntry(ievt)
            # If the weight is called "weight", then :
            # w[0] = ttree_f.weight/JZ_func
            # If the weight is called "weight_beamSpotWeight", then :
            # w[0] = ttree_f.weight_beamSpotWeight/JZ_func
            # If the weight is called "mcEventWeight", then :
            scale[0] = reweightFactor
            w[0] = ttree.weight/reweightFactor
            # if ( ttree_f.weight_pileup != 1.0) :
                # print(ttree_f.weight_beamSpotWeight ,ttree_f.weight_pileup, w_pileUP_x_beamSpot)
            b.Fill()
            b_scale.Fill()
        ttree.Write(opts.tree)
        # ttree.Write(opts.tree, ROOT.TObject.kOverwrite)
        fout.Close()
    return

def main():
    print('Getting r-tag and dsid for samples.')
    R_TAG, DSID = "", ""
    opts =  parseOptions() 
    for i in r_tag:
        if i in opts.directory:
            R_TAG = i
    for i in dsid:
        if i in opts.directory:
            DSID = i
    if DSID=='' or R_TAG == '':
        print('ERROR: Some of the r-tag or dsid is not found in the directory name.')
        print(f'Found values: R_TAG=[{R_TAG}], DSID=[{DSID}]')
        return
    if (opts.output[-1] == "/"):
            opts.output = opts.output[:-1]    
    
    if (opts.directory[-1] == "/"):
            opts.directory = opts.directory[:-1]   

    onlyfiles = [f for f in os.listdir(opts.directory) if os.path.isfile(os.path.join(opts.directory, f))]
    # print_files(onlyfiles, opts.directory)
    
    print('Getting reweight factor.')
    reweightFactor,reweightDict = accumulateReweightFactor(onlyfiles, opts.directory, opts, logPrint=False, outDict={'eventNumber':getEvntNum, 'eventWeight':getEvntWei, 'TotalWeight':getTotWe})
    print('rtag={}'.format(R_TAG),'dsid={}'.format(DSID),reweightFactor)
    print(reweightDict)
    print("Total reweight factor: ",reweightFactor)
    Init_N_Clean(opts,R_TAG,DSID)
    # createCopyJZ(onlyfiles, opts, fileIter=0)
    # addReweightBranch(onlyfiles, opts, reweightFactor=reweightDict['eventWeight'] ,fileIter=0)
    for fileIter in range(len(onlyfiles)):
        createCopyJZ(onlyfiles, opts, fileIter=fileIter)
        addReweightBranch(onlyfiles, opts, reweightFactor=reweightDict['eventWeight'] ,fileIter=fileIter)
    
    print(accumulateReweightFactor([f for f in os.listdir(opts.output) if os.path.isfile(os.path.join(opts.output, f))], opts.output, opts, logPrint=False, outDict={'eventNumber':getEvntNum,
    'TotalWeight':getTotWe,
    'TotalReWeight':getTotRWe,
    })[1])
    print(reweightDict)
    
    exit(0)
    return 

if __name__ == "__main__":
    main()
    
    print("+I+")
