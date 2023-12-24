import os, serial, sys, time, random, fnmatch

ScriptPath = os.path.dirname(os.path.abspath(__file__))
LibFolderName = "Libraries"

LibPath = os.path.join(ScriptPath, LibFolderName)
sys.path.insert(1, LibPath)

import InteractivePlot

def GetTestPathList(FolderPath):

    pattern = '*_AVGD.csv'

    TestList=[]

    for root, dirs, files in os.walk(FolderPath):
        for filename in fnmatch.filter(files, pattern):
            TestList.append(os.path.join(root, filename))

        return TestList

def func1():
    # Initialize my_plots dictionary
    my_plots = {"title": [], "fig": [], "zMin": [], "zMax": []}

    TestsPath= r'C:\Users\twalter\Desktop\ConverterCaracterization-dev\Output_Efficiency\SN000_10'

    TestsPathList = GetTestPathList(TestsPath)

    InteractivePlot.InteractivePlotEff3D(TestsPathList, 1, my_plots)

###################################################################
#                          Entry point                            #
###################################################################
if __name__ == "__main__":


    func1()