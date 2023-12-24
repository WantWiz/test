import os, sys, fnmatch

ScriptPath = os.path.dirname(os.path.abspath(__file__))
LibFolderName = "Libraries"

LibPath = os.path.join(ScriptPath, LibFolderName)
# caution: path[0] is reserved for script path (or '' in REPL)
# sys.path.insert(0, LibPath)
sys.path.insert(1, LibPath)

import InteractivePlot

###################################################################
#                          GetTestPathList                        #
###################################################################
def GetTestPathList(FolderPath):

    pattern = '*_AVGD.csv'

    TestList=[]

    for root, dirs, files in os.walk(FolderPath):
        for filename in fnmatch.filter(files, pattern):
            TestList.append(os.path.join(root, filename))

    return TestList

###################################################################
#                           GetUserChoice                         #
###################################################################
def GetUserChoice():
    print(" ______________________________________________ ")
    print("|            ------ MENU -----                 |")
    print("|    Enter 1 : 3D Efficiency                   |")
    print("|    Enter 2 : 3D Absolute error efficiency    |")
    print("|    Enter 3 : 3D Relative error efficiency    |")
    print("|    press 4 : 2D Absolute error power high    |")
    print("|    press 5 : 2D Relative error power high    |")
    print("|    press 6 : 2D Absolute error power low     |")
    print("|    press 7 : 2D Relative error power low     |")
    print("|______________________________________________|")

    tmpchoice = int(input())

    if(tmpchoice == 1):
        choice = "3DEff"
    elif(tmpchoice == 2):
        choice = "3DAbsEffErr"
    elif(tmpchoice == 3):
        choice = "3DRelEffErr"  
    elif(tmpchoice == 4):
        choice = "2DAbsErrPHigh"  
    elif(tmpchoice == 5):
        choice = "2DRelErrPHigh"
    elif(tmpchoice == 6):
        choice = "2DAbsErrPLow"  
    elif(tmpchoice == 7):
        choice = "2DRelErrPLow"  

    #Getting Low leg number
    LowLeg = int(input("Leg for low side :\n"))

    return choice, LowLeg

###################################################################
#                            routine                              #
###################################################################
def routine(TestPathList):

    Choice, LowLeg = GetUserChoice()

    if(Choice == "3DEff"):
        InteractivePlot.InteractivePlotEff3D(TestPathList, LowLeg)

    elif(Choice == "3DAbsEffErr"):
        InteractivePlot.InteractivePlot3DAbsEffErr(TestPathList, LowLeg)

    elif (Choice == "3DRelEffErr"):
        InteractivePlot.InteractivePlot3DRelEffErr(TestPathList, LowLeg)

    elif (Choice == "2DAbsErrPHigh"):
        InteractivePlot.InteractivePlot2DAbsErrPHigh(TestPathList)

    elif (Choice == "2DRelErrPHigh"):
        InteractivePlot.InteractivePlot2DRelErrPHigh(TestPathList)

    elif (Choice == "2DAbsErrPLow"):
        InteractivePlot.InteractivePlot2DAbsErrPLow(TestPathList, LowLeg)
    
    elif (Choice == "2DRelErrPLow"):
        InteractivePlot.InteractivePlot2DRelErrPLow(TestPathList, LowLeg)

###################################################################
#                              main                               #
###################################################################
def main(init):

    Continue = "y"

    if(init == 0):
        FolderPath = input("Paste the test result folder\n")
        init = 1

        TestPathList = GetTestPathList(FolderPath)

    routine(TestPathList)

###################################################################
#                          Entry point                            #
###################################################################
if __name__ == "__main__":

    init = 0
    main(init)