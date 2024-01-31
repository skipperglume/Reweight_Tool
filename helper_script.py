import glob
import argparse
import os,sys
parser = argparse.ArgumentParser(description="Quick transformation from string of floats to a comma separated")
parser.add_argument('--stringInput','-si',  type=str, default='0 0.9 1.2 1.5 1.8 2.4 2.8 3.2 3.5 4.0 4.3 4.9')
parser.add_argument('--dirInput','-di',  type=str, default='pass')




def getFileName(dir, result=None):
    if not result:
        result = set()
    if dir == 'pass':
        return None
    dir = dir.strip()
    if (not dir[0] =='/') and (not dir[0] =='.'):
        dir = './' + dir
    if not dir[-1] =='/':
        dir = dir + '/'
    if not os.path.exists:
        print(f'{dir} is not a valid path!')
        exit(1)
    if not os.path.isdir(dir):
        print(f'{dir} is not a valid directory!')
        exit(1)

    # print(dir)
    for name in glob.glob(dir+'*'):
        if os.path.isdir(name):
            # print(f'Is a directory: {name}')
            result = getFileName(name, result)
        if os.path.isfile(name):
            print(f'Is a file: {name}')
            result.add(name)
    
    return result

def vectorizeString(string)->str:
    print('Vectorized is:')
    string = string.strip()
    string = string.replace(' ',', ')
    
    print('{',string,'}')
    return string
if __name__ == '__main__':
    args = parser.parse_args()
    vectorizeString(args.stringInput)
    fileList = getFileName(args.dirInput)
    print(fileList)
    os.system('rm Custom_File_List.txt')
    for file in fileList:
        os.system(f'echo \"\'{file}\'\", >> Custom_File_List.txt')
        print("\'",file,"\',", sep='')
    exit(0)
# /eos/atlas/atlascerngroupdisk/perf-jets/JETDEF/MC23_SmallR_UFO_7GeV/MC23a/
