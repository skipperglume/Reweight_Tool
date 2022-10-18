dsid = ["364700", "364701", "364702", "364703", "364704",
"364705", "364706", "364707", "364708", "364709", 
"364710", "364711", "364712"]


dsid = ["364709","364710","364711","364712"]
dsid =  ["364700", "364701", "364702", "364703", "364704",
"364705", "364706", "364707", "364708", "364709", 
"364710", "364711", "364712"]
R_TAG = "MC20a"



def Cycle(R_TAG, dsid):
    print("cd /eos/user/d/dtimoshy/MC20_IJT")
    print("rm -rf ./*")
    for i in dsid:
        print("cd /eos/user/d/dtimoshy/MC20_IJT")
        print("rucio list-dids   user.dtimoshy:user.dtimoshy.{1}.{0}_{1}_150922_tree.root".format(R_TAG,i)  )
        print("rucio get   user.dtimoshy:user.dtimoshy.{1}.{0}_{1}_150922_tree.root".format(R_TAG,i)  )
        print("cd /afs/cern.ch/work/d/dtimoshy/Reweight_Tool")
        print("python3 reweight.py -d  /eos/user/d/dtimoshy/MC20_IJT/user.dtimoshy.{1}.{0}_{1}_150922_tree.root  -o   /eos/user/d/dtimoshy/__RWED__{0}".format(R_TAG,i))
        print("rm -rf  /eos/user/d/dtimoshy/MC20_IJT/user.dtimoshy.{1}.{0}_{1}_150922_tree.root".format(R_TAG,i)  )
        print()


def Group_Disk(R_TAG, dsid):
    for i in dsid:
        # print("python3 reweight.py -d  /eos/user/d/dtimoshy/MC20_IJT/user.dtimoshy.{1}.{0}_{1}_150922_tree.root  -o   /eos/user/d/dtimoshy/__RWED__{0}".format(R_TAG,i))
        print("python3 reweight.py -d   /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/Recs2022/NoCalib/group.perf-jets.{1}.{0}IJTR22v01_091022_tree.root  -o   /eos/user/d/dtimoshy/MC20_IJT_UFO/{0}".format(R_TAG,i))

if __name__ == "__main__":
    # Cycle(R_TAG,dsid) # For rucio -> reweight cycle
    Group_Disk(R_TAG,dsid)
