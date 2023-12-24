import os, csv, serial, pyvisa, time, sys

ScriptPath = os.path.dirname(os.path.abspath(__file__))
LibFolderName = "Libraries"

LibPath = os.path.join(ScriptPath, LibFolderName)
# caution: path[0] is reserved for script path (or '' in REPL)
# sys.path.insert(0, LibPath)
sys.path.insert(1, LibPath)

import Settings, EAPSI9750, K2000, bk8500, Plot, ActiveLoad
import FileMngt, SPIN_Comm, OrganizeDataInCSV, MonitoringMeasures
from pages import analyse_page

###################################################################
#                         GetUserChoice                           #
###################################################################
def GetUserChoice():
    print(" _______________________ ")
    print("|   ------ MENU -----   |")
    print("|    Enter 1 : VHigh    |")
    print("|    Enter 2 : IHigh    |")
    print("|    Enter 3 : VLow     |")
    print("|    press 4 : ILow     |")
    print("|    press 5 : All      |")
    print("|_______________________|")

    tmpchoice = int(input())

    if(tmpchoice == 1):
        choice = "VHigh"
    elif(tmpchoice == 2):
        choice = "IHigh"
    elif(tmpchoice == 3):
        choice = "VLow"  
    elif(tmpchoice == 4):
        choice = "ILow"  
    elif(tmpchoice == 5):
        choice = "All"  
    return choice

###################################################################
#                          VHighSweep                             #
###################################################################
def VHighSweep(Choice, PowerSupply, STLINK, TestPath, DMMDict):

    print("****Starting VHigh measures****")

    for i in range(0,(Settings.json_data["AccNumberOfVHighStep"]),1):#for(x,y,z) number of iteration = y-x. z = step size (default = 1)
        Settings.TestAccuracyProgress+=1

        print("\n ***VHigh step number : ", i)

        VHighStep_mV = Settings.json_data["AccVHighStepArray_mV"][i]
        PowerSupply.setVoltage_mV(VHighStep_mV)
        
        SPIN_Comm.FlushSerialBuffer(STLINK)

        for i in range(1,(Settings.json_data["NumberOfPointsPerDuty"]+1),1):
            MonitoringMeasures.GetDMMSingleMeasSerialMeasAndSaveItInCSV(Choice, STLINK, TestPath, DMMDict)

###################################################################
#                          VLowSweep                              #
###################################################################
def VLowSweep(Choice, ActiveLoadObj, STLINK, TestPath, DMMDict):

    Duty_Percent = Settings.json_data["starting_duty_cycle_Percent"]

    SPIN_Comm.InitDutySweep(STLINK)

    SPIN_Comm.FlushUntilExpectedDuty(STLINK, Settings.json_data["starting_duty_cycle_Percent"])

    for i in range(0, Settings.json_data["NumberOfPointsPerDuty"], 1):
        print("Reading: ", i)

        MonitoringMeasures.GetDMMSingleMeasSerialMeasAndSaveItInCSV(Choice, STLINK, TestPath, DMMDict)

    for i in range(0, Settings.json_data["AccNumberOfStepInVLowDutySweep"], 1):

        Settings.TestAccuracyProgress+=1

        print("Sending u :", (i))

        STLINK.write(b'u')
        time.sleep(1)#Time for set point to establish

        Duty_Percent+=Settings.json_data["duty_step_Percent"]
        SPIN_Comm.FlushUntilExpectedDuty(STLINK, Duty_Percent)

        for i in range(0, Settings.json_data["NumberOfPointsPerDuty"], 1):
            print("Reading: ", i)
            MonitoringMeasures.GetDMMSingleMeasSerialMeasAndSaveItInCSV(Choice, STLINK, TestPath, DMMDict)
    
    SPIN_Comm.ExitDutySweep(STLINK)

###################################################################
#                          ILowSweep                              #
###################################################################
def ILowSweep(Choice, ActiveLoadObj, STLINK, TestPath, DMMDict):
    
    print("****Starting ILow measures****")

    STLINK.write(b'p')

    for i in range(0,(Settings.json_data["AccILowNumberOfCurrentStep"]),1):#for(x,y,z) number of iteration = y-x. z = step size (default = 1)

        Settings.TestAccuracyProgress+=1

        print("\n ***Current step number : ", i)
    
        CurrentSentToLoad_A = (Settings.json_data["AccILowCurrentStepArray_mA"][i]/(Settings.MilliToUnitConversionRatio))
        ActiveLoad.SetCurrent_A(ActiveLoadObj, Settings.ActiveLoadAddress, CurrentSentToLoad_A)
        SPIN_Comm.FlushSerialBuffer(STLINK)

        for i in range(1,(Settings.json_data["NumberOfPointsPerDuty"]+1),1):
            MonitoringMeasures.GetDMMSingleMeasSerialMeasAndSaveItInCSV(Choice, STLINK, TestPath, DMMDict)

###################################################################
#                          IHighSweep                             #
###################################################################
def IHighSweep(Choice, ActiveLoadObj, STLINK, TestPath, DMMDict):
    
    print("****Starting IHigh measures****")

    STLINK.write(b'p')

    for i in range(0,(Settings.json_data["AccIHighNumberOfCurrentStep"]),1):#for(x,y,z) number of iteration = y-x. z = step size (default = 1)

        Settings.TestAccuracyProgress+=1

        print("\n ***Current step number : ", i)
        CurrentSentToLoad_A = ((Settings.json_data["AccIHighCurrentStepArray_mA"][i])/(Settings.MilliToUnitConversionRatio))
        ActiveLoad.SetCurrent_A(ActiveLoadObj, Settings.ActiveLoadAddress, CurrentSentToLoad_A)
        SPIN_Comm.FlushSerialBuffer(STLINK)

        for i in range(1,(Settings.json_data["NumberOfPointsPerDuty"]+1),1):
            MonitoringMeasures.GetDMMSingleMeasSerialMeasAndSaveItInCSV(Choice, STLINK, TestPath, DMMDict)

###################################################################
#                  SetCalibrationWorkingPoints                    #
###################################################################
def SetCalibrationWorkingPoints(ActiveLoadObj, STLINK, Choice, PowerSupply):
    STLINK.write(b'p')
    if(Choice == "VHigh"):
        SPIN_Comm.SetTWISTDutyCycle(STLINK, Settings.json_data["starting_duty_cycle_Percent"], Settings.json_data["duty_step_Percent"], Settings.json_data["AccVHighCalibrationDutyPercent"])
        CurrentSentToLoad_A = ((Settings.json_data["AccVHighCalibrationLowCurrent_mA"])/(Settings.MilliToUnitConversionRatio))
        ActiveLoad.SetCurrent_A(ActiveLoadObj, Settings.ActiveLoadAddress, CurrentSentToLoad_A)

    elif(Choice == "IHigh"):
        SPIN_Comm.SetTWISTDutyCycle(STLINK, Settings.json_data["starting_duty_cycle_Percent"], Settings.json_data["duty_step_Percent"], Settings.json_data["AccIHighCalibrationDuty_Percent"])
        PowerSupply.setVoltage_mV(Settings.json_data["AccIHighCalibrationVHigh_mV"])

    elif(Choice == "VLow"):
        CurrentSentToLoad_A = ((Settings.json_data["AccVLowCalibrationLowCurrent_mA"])/(Settings.MilliToUnitConversionRatio))
        ActiveLoad.SetCurrent_A(ActiveLoadObj, Settings.ActiveLoadAddress, CurrentSentToLoad_A)
        PowerSupply.setVoltage_mV(Settings.json_data["AccVLowCalibrationVHigh_mV"])

    elif(Choice == "ILow"):
        SPIN_Comm.SetTWISTDutyCycle(STLINK, Settings.json_data["starting_duty_cycle_Percent"], Settings.json_data["duty_step_Percent"], Settings.json_data["AccILowCalibrationDuty_Percent"])
        PowerSupply.setVoltage_mV(Settings.json_data["AccILowCalibrationVHigh_mV"])

    
    time.sleep((Settings.TimeWaitedForSteadyStateReach_Reset_ms)/1000)#Steady state reach delay

##################################################################
#                           InitTest                             #
##################################################################
def InitTest(STLINK, PowerSupply, TestFolder, TestName, Choice, ActiveLoadObj):

    TestPath = TestFolder + '/'  + TestName + "_" + Choice + '.csv'
    OrganizeDataInCSV.SaveHeaderAcc(Choice, TestPath, Settings.AccHeaderDict)
    PowerSupply.init()

    SetCalibrationWorkingPoints(ActiveLoadObj, STLINK, Choice, PowerSupply)

    return TestPath

###################################################################
#                         AccuracyRoutine                         #
###################################################################
def AccuracyRoutine(ActiveLoadObj, PowerSupply, STLINK, TestPath, Choice, LowLeg, DMMDict, Disp):

    if(Choice == "VHigh"):
        VHighSweep(Choice, PowerSupply, STLINK, TestPath, DMMDict)
        AVGDFilePath = OrganizeDataInCSV.AverageBlockAndStdDev(TestPath, Settings.json_data["NumberOfPointsPerDuty"])

    elif(Choice == "IHigh"):
        IHighSweep(Choice, ActiveLoadObj, STLINK, TestPath, DMMDict)
        AVGDFilePath = OrganizeDataInCSV.AverageBlockAndStdDev(TestPath, Settings.json_data["NumberOfPointsPerDuty"])
    
    elif(Choice == "VLow"):
        VLowSweep(Choice, ActiveLoadObj, STLINK, TestPath, DMMDict)
        AVGDFilePath = OrganizeDataInCSV.AverageBlockAndStdDev(TestPath, Settings.json_data["NumberOfPointsPerDuty"])

    elif(Choice == "ILow"):
        ILowSweep(Choice, ActiveLoadObj, STLINK, TestPath, DMMDict)
        AVGDFilePath = OrganizeDataInCSV.AverageBlockAndStdDev(TestPath, Settings.json_data["NumberOfPointsPerDuty"])
    OrganizeDataInCSV.ComputeAndSaveErrors(Choice, AVGDFilePath, LowLeg)

    Plot.CreateGraphErrorSingle(Choice, AVGDFilePath, "A", Settings.json_data["NumberOfPointsPerDuty"], Disp, LowLeg)
    Plot.CreateGraphErrorSingle(Choice, AVGDFilePath, "R",  Settings.json_data["NumberOfPointsPerDuty"], Disp, LowLeg)

    return AVGDFilePath

##################################################################
#                        MeasureAccuracy                         #
##################################################################
def MeasureAccuracy(TestName, LowLeg):

    Settings.TestAccuracyProgress+=1

    LowLeg = int(LowLeg)
    Choice = "All"
    #Connect INSTRUMENTS
    ResourceManager = pyvisa.ResourceManager()
    IHigh = K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.IHighGPIBAddress))
    VHigh = K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.VHighGPIBAddress))
    VLow = K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.VLowGPIBAddress))
    ILow = K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.ILowGPIBAddress))

    PowerSupply = EAPSI9750.EAPSI9750(ResourceManager.open_resource(Settings.PSUCommPort))
    STLINK = serial.Serial(Settings.STLINKCommPort)
    ActiveLoadObj = serial.Serial(Settings.ActiveLoadCommPort)
    
    #Init serial objects
    SPIN_Comm.InitSerialObjectTimeout(STLINK, Settings.STLINKbaudRate, Settings.STLINKbytesize,\
        Settings.STLINKparity, Settings.STLINKstopbits, Settings.STLINKTimeout_s)
    ActiveLoad.Init(ActiveLoadObj, Settings.ActiveLoadbaudRate, Settings.ActiveLoadparity,\
        Settings.ActiveLoadsTimeout)

    ActiveLoad.SetSafetySettings(ActiveLoadObj, Settings.ActiveLoadAddress,\
    Settings.json_data["LoadInternalSafetyCurrent_A"], Settings.json_data["LoadInternalSafetyPower_W"])
    # SPIN_Comm.SetCoefficients(STLINK, Settings.CalibrationCoeffs)
    #Dictionnary of DMM
    DMMDict =	{
    "IHigh": IHigh,
    "VHigh": VHigh,
    "VLow": VLow,
    "ILow": ILow,
    }

    #Dictionnary of tests results path
    CSVResultsDict = {}

    #Test infos
    # if(debug == 1):
    #     Choice = "All"
    #     TestName = "Debug"

    # elif(debug == 0):
    #     Choice = GetUserChoice()
    #     TestName = input("Test name : \n")
    Dir = os.path.dirname(os.path.abspath(__file__))
    Dir = os.path.join(Dir, "Results")
    Dir = os.path.join(Dir, TestName)
    TestFolder = FileMngt.CreateSubfolder(Dir, "Output_Accuracy")

    # if(Choice == "All"):
    ChoiceTab = ["VHigh", "IHigh", "VLow", "ILow"]

    # if (debug == 1):

    #     LowLeg = 1

    # elif (debug == 0):

        # LowLeg = int(input("Side for Low voltage and current measure (1/2): \n"))
        # LowLeg = int(LowLeg)

    for Choice in ChoiceTab:

        TestPath = InitTest(STLINK, PowerSupply, TestFolder, TestName, Choice, ActiveLoadObj)
        # TestPathFolder = os.path.dirname(TestPath)
        # TestPath = TestPathFolder + "/" + TestName + "_" + Choice + ".cvs"
        AccuracyRoutine(ActiveLoadObj, PowerSupply, STLINK, TestPath, Choice, LowLeg, DMMDict, "NoDisp")

        TestPathNoExt, file_extension = os.path.splitext(TestPath)

        TestPathAVG = TestPathNoExt + '_AVGD.csv'

        CSVResultsDict[Choice] = TestPathAVG

    Plot.PlotAllAccuracyGraphs(CSVResultsDict, Settings.json_data["NumberOfPointsPerDuty"], LowLeg)
    
    # else:

    #     if(Choice == "VLow"):
    #         LowLeg = input("Side for Low voltage measure (1/2): \n")

    #     elif(Choice == "ILow"):
    #         LowLeg = input("Side for Low current measure (1/2): \n")
    #         LowLeg = int(LowLeg)

    #     else:
    #         #If choice is not VLow or ILow, LowLeg must be initialized
    #         LowLeg = 1

    #     TestPath = InitTest(STLINK, PowerSupply, TestFolder, TestName, Choice, ActiveLoadObj)

    #     AccuracyRoutine(ActiveLoadObj, PowerSupply, STLINK, TestPath, Choice, LowLeg, DMMDict, "Disp")

    #Exiting power supply remote and setting safe voltage
    PowerSupply.exit()

    #Disabling load remote control and set current to 0
    bk8500.enable_input(ActiveLoadObj, Settings.ActiveLoadAddress, False)
    bk8500.set_current(ActiveLoadObj, Settings.ActiveLoadAddress, 0)
    bk8500.set_remote(ActiveLoadObj, Settings.ActiveLoadAddress, False)

    #Setting TWIST in idle and reset duty for the exit of the test
    STLINK.write(b'i')
    STLINK.write(b'r')
    STLINK.close()
    
    Settings.TestAccuracyProgress+=1

###################################################################
#                              main                               #
###################################################################
def main():
    debug = 0 #1 for debug mode, 0 for normal mode

    start_time=time.time()

    MeasureAccuracy(TestName, LowLeg)
    
    end_time=time.time()
    elapsed=end_time-start_time

    print("Elapsed:\n", elapsed)

###################################################################
#                          Entry point                            #
###################################################################
if __name__ == "__main__":

    main()
