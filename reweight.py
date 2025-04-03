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
    # parser.add_argument('-w','--weight', default='sumw', help="Normalise by 'nevts' or 'sumw'")
    # parser.add_argument('-b','--branch', default="weight", type=str, help="Branch of event's weight")
    parser.add_argument('-test','--test', action='store_true', help="Run the small subset of all files")
    args = parser.parse_args()
    return args

def printDirectoryFiles(fileContent:list, directory:str)->None:
    '''
    Method to print the files in a directory
    '''
    print(f'The directory: [{directory}] has [{len(fileContent)}] files:')
    for fileNameIter in range(len(fileContent)):
        fileName = fileContent[fileNameIter]
        print(f' - [{fileNameIter+1}/{len(fileContent)}] : {fileName}')

def getEvntNum(inputTTree, inputHist):
    '''
    Return the number of events in the input TTree
    '''
    return inputTTree.GetEntries()

def getEvntWei(inputTTree, inputHist):
    '''
    Return the event weight from the input TTree
    It is assumed 3rd bin of the histogram is the event weight for the whole tree
    '''
    return inputHist.GetBinContent(3)

def getTotWe(inputTTree, inputHist):
    '''
    Iterate over the TTree and sum the event weights "weight"
    '''
    result = 0 
    inputTTree.SetBranchStatus("*",0)
    inputTTree.SetBranchStatus("weight",1)

    nEntries = inputTTree.GetEntries()
    for ievt in range(nEntries):
        inputTTree.GetEntry(ievt)
        result += inputTTree.weight
        # print(inputTTree)
        # print(type(inputTTree))
        # print(f'{ievt} : {inputTTree.weight}')
    inputTTree.SetBranchStatus("*",1)
    return result

def getTotRWe(inputTTree, inputHist):
    '''
    Iterate over the TTree and sum the reweighted event weights "R_weight"
    '''
    result = 0 
    inputTTree.SetBranchStatus("*",0)
    inputTTree.SetBranchStatus("R_weight",1)

    nEntries = inputTTree.GetEntries()
    for ievt in range(nEntries):
        inputTTree.GetEntry(ievt)
        result += inputTTree.R_weight

    inputTTree.SetBranchStatus("*",1)
    return result

def accumulateReweightFactor(fileNamesList:list, dir:dir, opts, outDict:dict, logPrint:bool=True):
    '''
    Method to accumulate the reweight factor from the input files
    '''
    result = 0 # Sum of the event weights
    resultDict = {}
    for name in outDict.keys():
        resultDict[name] = 0 
    if logPrint:    print('start',resultDict)
    
    print('Accumulating ')
    for fileName in fileNamesList:
        if (fileName[-5:] == ".part"):
            continue
        
        f_in = ROOT.TFile.Open(dir+'/'+fileName,"read")    
        TTree_f = f_in.Get(opts.tree)
        
        if ( TTree_f != None and fileName[-6:-1] != ".part"):
            THisto_f = f_in.Get(opts.hist)
            if THisto_f:
                result += THisto_f.GetBinContent(3)
            if logPrint: print(fileName, TTree_f.GetEntries(), THisto_f.GetBinContent(3))
            for var in outDict.keys():
                resultDict[var] += outDict[var](TTree_f, THisto_f)
        
        f_in.Close()
    if logPrint: print('end',resultDict)
    return (result, resultDict)

def initAndCleanOutput(opts, R_TAG, DSID):
    '''
    Initialize the output directory and clean it if it exists
    Also modifies the output directory to include the specific folder of R_TAG and DSID combination
    '''
    
    print(f'Creating output directory: {opts.output}')
    if not os.path.exists(opts.output):
        os.system(f'mkdir -p {opts.output}')
    
    opts.output = f'{opts.output}/{R_TAG}_{DSID}' 
    
    if os.path.exists(opts.output):
        os.system(f'rm -rf {opts.output}')
    os.system(f'mkdir -p {opts.output}')
    print(f'Folder of reweighted ntuples: [{opts.output}]')
    return 

def createCopyJZ(fileName:str, opts)->str:
    '''
    Creates a copy of a ntuple ROOT file
    '''
    
    if (fileName[-5:] == '.part'):
        ERROR_print(f'File is not finished downloading: [{fileName}]')
        
    fileInput = ROOT.TFile.Open(f'{opts.directory}/{fileName}', 'read') # open the file
    treeInput = fileInput.Get(opts.tree) # get the TTree
    if ( treeInput == None ):
        ERROR_print(f'TTree in file is None: [{fileName}]')
    
    treeInput.SetBranchStatus('*',1)
    treeInput.SetBranchStatus('jet_ConstitE',0)
    treeInput.SetBranchStatus('jet_Jvt',0)
    
    # Write ttree to new output file
    pathToOutput = f'{opts.output}/__reweighted__{fileName}'
    print(f'Creating output file: [{pathToOutput}]')
    if os.path.exists(pathToOutput):
        os.system(f'rm -rf {pathToOutput}')
    
    fout = ROOT.TFile(pathToOutput, 'create')
    fout.cd()
    Reweighted_ttree = treeInput.CloneTree()
    fileInput.Close()
    Reweighted_ttree.Write()
    fout.Close()
    return pathToOutput

def addReweightBranch(fileName:str, opts, reweightFactor:iter=0):
    '''
    Add a new branch (named R_weight) to the output file
    '''
    
    path_to_output = f'{opts.output}/__reweighted__{fileName}'
    print(f'Adding new branch to: [{path_to_output}]')
    fout = ROOT.TFile.Open(path_to_output, "update")
    ttree = fout.Get(opts.tree)

    ttree.SetBranchStatus("*", 1)
    ttree.SetBranchStatus("weight", 1)
    w = array('d', [-1])
    b = ttree.Branch("R_weight", w, "R_weight/D")
    scale = array('d', [-1])
    b_scale = ttree.Branch("sumw", scale, "sumw/D")
    
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
    ttree.Write(opts.tree) # ttree.Write(opts.tree, ROOT.TObject.kOverwrite)
    
    fout.Close()
    return

def printOutDict(outDict:dict)->None:
    '''
    Print the output dictionary
    '''
    for key in outDict.keys():
        print(f' - {key} : {outDict[key]}')

def main():
    '''
    Main function to run the reweighting tool.
    Creates output folder, copies the input files, and adds the reweight branch.
    '''
    print('Getting r-tag and dsid for samples.')
    R_TAG, DSID = "", ""
    opts =  parseOptions() 
    for i in r_tag:
        if i in opts.directory:
            R_TAG = i
    for i in dsid:
        if i in opts.directory:
            DSID = i
    print(f'Found values: R_TAG=[{R_TAG}], DSID=[{DSID}]')
    if DSID=='' or R_TAG == '':
        print('ERROR: Some of the r-tag or dsid is not found in the directory name.')
        return
    
    # Check if the directory exists
    opts.output = opts.output.rstrip("/") # Remove trailing slash
    opts.directory = opts.directory.rstrip("/") # Remove trailing slash

    onlyfiles = [f for f in os.listdir(opts.directory) if os.path.isfile(os.path.join(opts.directory, f))]
    printDirectoryFiles(onlyfiles, opts.directory)
    
    print('Getting reweight factor.')
    processDict = {'eventNumber':getEvntNum, 'eventWeight':getEvntWei, 'TotalWeight':getTotWe}
    reweightFactor, reweightDict = accumulateReweightFactor(
        onlyfiles, 
        opts.directory, 
        opts, 
        logPrint=False, 
        outDict=processDict,
    )
    print(f'rtag : [{R_TAG}] ; dsid : [{DSID}]')
    print(f'Evaluated Reweight Factor : [{reweightFactor}]')
    printOutDict(reweightDict)
    
    # Initialize the output directory
    initAndCleanOutput(opts, R_TAG, DSID)
    
    nFiles = len(onlyfiles)
    if opts.test: # In Test mode - run few files
        nFiles = min(1, nFiles)
    
    print('=== Processing files ===')
    for fileIter in range(nFiles):
        fileName = onlyfiles[fileIter]
        print(f' - [{fileIter+1}/{nFiles}] Processing file path: [{fileName}]')
        # createCopyJZ(fileName, opts) # Create a copy of the file
        # addReweightBranch(filePath, opts, reweightFactor=reweightDict['eventWeight']) # Add the reweight branch
    
    filesReweightedList = [f for f in os.listdir(opts.output) if os.path.isfile(os.path.join(opts.output, f))]
    postProcessDict = {'eventNumber':getEvntNum, 'TotalWeight':getTotWe, 'TotalReWeight':getTotRWe}
    reweightFactorPost, reweightDictPost = accumulateReweightFactor(
            filesReweightedList, 
            opts.output, 
            opts, 
            logPrint=False, 
            outDict=postProcessDict,
        )
    print(f'rtag : [{R_TAG}] ; dsid : [{DSID}]')
    print(f'Post Process Reweight Factor : [{reweightFactorPost}]')
    printOutDict(reweightDictPost)
    
    return

if __name__ == "__main__":
    main()
    
    print("+I+")
