import os

###################################################################
#                   CreateSubfolder                               #
###################################################################
def CreateSubfolder(RootFolderDir, NewFolderName):
    Dir = os.path.join(RootFolderDir, NewFolderName)

    if not os.path.exists(Dir):
        os.makedirs(Dir)
    return Dir

###################################################################
#                   CreateListOfAveragedTestsResults              #
###################################################################
def CreateListOfAveragedTestsResults(PathLists):
    
    PathListsAVGD = ['']*len(PathLists)
    for i, path in enumerate(PathLists):
        dir_path, filename = os.path.split(path)
        new_filename = os.path.splitext(filename)[0] + '_AVGD.csv'
        new_path = os.path.join(dir_path, new_filename)
        PathListsAVGD[i] = new_path
    return PathListsAVGD