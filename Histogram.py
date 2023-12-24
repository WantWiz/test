import os, csv, serial, pyvisa, time, sys

ScriptPath = os.path.dirname(os.path.abspath(__file__))
LibFolderName = "Libraries"

LibPath = os.path.join(ScriptPath, LibFolderName)
# caution: path[0] is reserved for script path (or '' in REPL)
# sys.path.insert(0, LibPath)
sys.path.insert(1, LibPath)

import Settings, EAPSI9750, K2000, bk8500, Plot, ActiveLoad
import FileMngt, SPIN_Comm, OrganizeDataInCSV, MonitoringMeasures
from pages import setup_page
import pandas as pd
import numpy as np
import json

###################################################################
#                          VHighSweep                             #
###################################################################
def VHighSweep(Choice, PowerSupply, STLINK, TestPath, DMMDict):

    print("****Starting VHigh measures****")

    for i in range(0,(Settings.json_data["HistNumberOfVHighStep"]),1):#for(x,y,z) number of iteration = y-x. z = step size (default = 1)


        print("\n ***VHigh step number : ", i)

        VHighStep_mV = Settings.json_data["HistVHighStepArray_mV"][i]
        PowerSupply.setVoltage_mV(VHighStep_mV)
        
        SPIN_Comm.FlushSerialBuffer(STLINK)

        for j in range(1,(Settings.json_data["HistNumberOfPointsPerDuty"]+1),1):
            Settings.TestHistogramProgress+=1
            MonitoringMeasures.GetDMMSingleMeasSerialMeasAndSaveItInCSV(Choice, STLINK, TestPath[i], DMMDict)

###################################################################
#                  SetCalibrationWorkingPoints                    #
###################################################################
def SetCalibrationWorkingPoints(ActiveLoadObj, STLINK, Choice, PowerSupply):

    STLINK.write(b'p')

    SPIN_Comm.SetTWISTDutyCycle(STLINK, Settings.json_data["starting_duty_cycle_Percent"], Settings.json_data["duty_step_Percent"], Settings.json_data["HistVHighCalibrationDutyPercent"])
    CurrentSentToLoad_A = ((Settings.json_data["HistVHighCalibrationLowCurrent_mA"])/(Settings.MilliToUnitConversionRatio))
    ActiveLoad.SetCurrent_A(ActiveLoadObj, Settings.ActiveLoadAddress, CurrentSentToLoad_A)

    time.sleep((Settings.TimeWaitedForSteadyStateReach_Reset_ms)/1000)#Steady state reach delay

##################################################################
#                           InitTest                             #
##################################################################
def InitTest(STLINK, PowerSupply, TestFolder, TestName, Choice, ActiveLoadObj):

    TestPath=[]
    for i in range(Settings.json_data["HistNumberOfVHighStep"]): 
        TestPath.append(TestFolder + '/'  + TestName + "_" + str(int(Settings.json_data["HistVHighStepArray_mV"][i]/1000)) + '.csv')
        OrganizeDataInCSV.SaveHeaderAcc(Choice, TestPath[i], Settings.HistHeaderDict)
    PowerSupply.init()

    SetCalibrationWorkingPoints(ActiveLoadObj, STLINK, Choice, PowerSupply)

    return TestPath

###################################################################
#                        HistogramRoutine                         #
###################################################################
def HistogramRoutine(ActiveLoadObj, PowerSupply, STLINK, TestPath, LowLeg, DMMDict, Disp, Choice):

    VHighSweep(Choice, PowerSupply, STLINK, TestPath, DMMDict)

##################################################################
#                        MeasureHistogram                        #
##################################################################
def MeasureHistogram(TestName, LowLeg):

    Settings.TestHistogramProgress+=1

    LowLeg = int(LowLeg)
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

    #Dictionnary of DMM
    DMMDict =	{
    "IHigh": IHigh,
    "VHigh": VHigh,
    "VLow": VLow,
    "ILow": ILow,
    }

    Dir = os.path.dirname(os.path.abspath(__file__))
    Dir = os.path.join(Dir, "Results")
    Dir = os.path.join(Dir, TestName)
    TestFolder = FileMngt.CreateSubfolder(Dir, "Output_Histogram")

    Choice = "VHigh"

    TestPath = InitTest(STLINK, PowerSupply, TestFolder, TestName, Choice, ActiveLoadObj)

    HistogramRoutine(ActiveLoadObj, PowerSupply, STLINK, TestPath, LowLeg, DMMDict, "NoDisp", Choice)

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
    
    # save the mean values and stanadart deviation un a csv
    # path of the results of the test 
    # one path matches with a voltage point
    Dir = os.path.dirname(os.path.abspath(__file__))
    OutputHistogramFolder = os.path.join(Dir, "Results")
    TestFolder = FileMngt.CreateSubfolder(OutputHistogramFolder, Settings.JsonTestsHistory_data["TestNamesHistory"][setup_page.TestIndex])
    TestFolder = FileMngt.CreateSubfolder(TestFolder, "Output_Histogram")
    PathResultsList=[TestFolder + '/' + Settings.JsonTestsHistory_data["TestNamesHistory"][setup_page.TestIndex] + "_" + str(Settings.JsonTestsHistory_data["HistVHighStepArray_mV_history"][setup_page.TestIndex][0]) + ".csv",
                        TestFolder + '/' + Settings.JsonTestsHistory_data["TestNamesHistory"][setup_page.TestIndex] + "_" + str(Settings.JsonTestsHistory_data["HistVHighStepArray_mV_history"][setup_page.TestIndex][1]) + ".csv",
                        TestFolder + '/' + Settings.JsonTestsHistory_data["TestNamesHistory"][setup_page.TestIndex] + "_" + str(Settings.JsonTestsHistory_data["HistVHighStepArray_mV_history"][setup_page.TestIndex][2]) + ".csv"]
    OutputHistogramFolder=os.path.join(OutputHistogramFolder, "Histo_Test_History")
    OutputHistogramFolder=os.path.join(OutputHistogramFolder, "LEG_" + str(Settings.JsonTestsHistory_data["LowLegHistory"][setup_page.TestIndex]))
    PathDataHistoryList=[OutputHistogramFolder + "/Histo_Test_History_" + str(Settings.JsonTestsHistory_data["HistVHighStepArray_mV_history"][setup_page.TestIndex][0]) + "V.csv",
                        OutputHistogramFolder + "/Histo_Test_History_" + str(Settings.JsonTestsHistory_data["HistVHighStepArray_mV_history"][setup_page.TestIndex][1]) + "V.csv",
                        OutputHistogramFolder + "/Histo_Test_History_" + str(Settings.JsonTestsHistory_data["HistVHighStepArray_mV_history"][setup_page.TestIndex][2]) + "V.csv"]

    for i in range(len(PathResultsList)):

        # read the appropriate csv
        df = pd.read_csv(PathResultsList[i], delimiter='\t')

        # remove the colums that contains the values of DMM VHigh and duty cycle
        df = df.drop(df.columns[0], axis=1) 
        df = df.drop(df.columns[0], axis=1)
        # we put the columns in the best order for the display of the histograms
        df.iloc[:, [1, 2]] = df.iloc[:, [2, 1]].values
        df.iloc[:, [1, 3]] = df.iloc[:, [3, 1]].values
        column_names = df.columns.tolist()
        column_names[1], column_names[2] = column_names[2], column_names[1]
        column_names[1], column_names[3] = column_names[3], column_names[1]
        df.columns = column_names
        list_values=[round(np.mean(df[column_names[0]])), round(np.std(df[column_names[0]])), 
                round(np.mean(df[column_names[1]])), round(np.std(df[column_names[1]])),
                round(np.mean(df[column_names[2]])), round(np.std(df[column_names[2]])),
                round(np.mean(df[column_names[3]])), round(np.std(df[column_names[3]])),
                round(np.mean(df[column_names[4]])), round(np.std(df[column_names[4]])),
                round(np.mean(df[column_names[5]])), round(np.std(df[column_names[5]]))]

        # write a new line in the appropriate csv with the mean and standart deviation obtained 
        with open(PathDataHistoryList[i] , 'a', newline='', encoding='UTF8') as file:

            writer = csv.writer(file, delimiter='\t')

            # Append a row with the specified values and save them in csv
            writer.writerow(list_values)
        
    Settings.TestHistogramProgress+=1


###################################################################
#                              main                               #
###################################################################
def main():
    debug = 0 #1 for debug mode, 0 for normal mode

    start_time=time.time()

    MeasureHistogram(TestName, LowLeg)
    
    end_time=time.time()
    elapsed=end_time-start_time

    print("Elapsed:\n", elapsed)

###################################################################
#                          Entry point                            #
###################################################################
if __name__ == "__main__":

    main()
