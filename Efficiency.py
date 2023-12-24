import os, csv, serial, pyvisa, time, sys

ScriptPath = os.path.dirname(os.path.abspath(__file__))
LibFolderName = "Libraries"

LibPath = os.path.join(ScriptPath, LibFolderName)
# caution: path[0] is reserved for script path (or '' in REPL)
# sys.path.insert(0, LibPath)
sys.path.insert(1, LibPath)

import Settings, EAPSI9750, K2000, bk8500, Plot, ActiveLoad
import FileMngt, SPIN_Comm, OrganizeDataInCSV

###################################################################
#                        MeasureEfficiency                        #
###################################################################
def MeasureEfficiency(TestName, LowLeg):

    Settings.TestEfficiencyProgress+=1

    # VHighTab_V = [10,20,30]
    # TestName = "TEST"
    # LowLeg = 2

    #Connect INSTRUMENTS
    ResourceManager = pyvisa.ResourceManager()
    IHigh = K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.IHighGPIBAddress))
    VHigh = K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.VHighGPIBAddress))
    VLow = K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.VLowGPIBAddress))
    ILow = K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.ILowGPIBAddress))

    #Dictionnary of DMM
    DMMDict =	{
    "IHigh": IHigh,
    "VHigh": VHigh,
    "VLow": VLow,
    "ILow": ILow,
    }

    PowerSupply = EAPSI9750.EAPSI9750(ResourceManager.open_resource(Settings.PSUCommPort))
    STLINK = serial.Serial(Settings.STLINKCommPort)
    ActiveLoadObj = serial.Serial(Settings.ActiveLoadCommPort)

    #Init serial objects
    SPIN_Comm.InitSerialObjectTimeout(STLINK, Settings.STLINKbaudRate, Settings.STLINKbytesize,\
        Settings.STLINKparity, Settings.STLINKstopbits, Settings.STLINKTimeout_s)
    ActiveLoad.Init(ActiveLoadObj, Settings.ActiveLoadbaudRate, Settings.ActiveLoadparity,\
        Settings.ActiveLoadsTimeout)
    
    # LowLeg = 1
    #If we are in debug, don't request test infos (time saving)
    # if(debug == 1):
    #     TestName = "Debug"
    #     LowLeg = 1
    #     VHighCount = 1
    # elif(debug == 0):
    #     TestName = input("Test name : \n")
    #     LowLeg = int(input("Side for Low voltage and current measure (1/2): \n"))
    #     VHighCount = int(input("Number of VHigh points : "))

    # creating an empty list for VHigh
    # VHighTab_V = []

    # iterating so we get all Vhigh points
    # for i in range(0, VHighCount):

    #     if(debug == 1):
    #         VoltHigh_V = 40

    #     elif(debug == 0):
    #         msg = "Enter VHigh value for test point number : " + str(i+1) + " in Volts (V): \n"
    #         VoltHigh_V = int(input(msg))

    #     VHighTab_V.append(VoltHigh_V) # adding the element

    # Create subfolder of test name  "Output_Efficiency" folder at root of script
    Dir = os.path.dirname(os.path.abspath(__file__))
    Dir = os.path.join(Dir, "Results")
    Dir = os.path.join(Dir, TestName)
    TestFolder = FileMngt.CreateSubfolder(Dir, "Output_Efficiency")
    # creating an empty list for tests path
    PathLists = []

    #Initialize Power supply
    PowerSupply.init()

    #Set active load safety settings
    ActiveLoad.SetSafetySettings(ActiveLoadObj, Settings.ActiveLoadAddress,\
    Settings.json_data["LoadInternalSafetyCurrent_A"], Settings.json_data["LoadInternalSafetyPower_W"])
    print(Settings.json_data["EffVHighStepArray_mV"])
    for EffVHighStep_mV in Settings.json_data["EffVHighStepArray_mV"]:

        EffVHighStep_mV = int(EffVHighStep_mV / 1000)
        print(EffVHighStep_mV)
        #Creating csv results files 
        tmp = os.path.join(TestFolder, TestName)
        CSVPath = tmp + "_" + str(EffVHighStep_mV) + 'V.csv'
        PathLists.append(CSVPath)
        OrganizeDataInCSV.SaveHeader(CSVPath, Settings.SavedCSVHeader)

        #Setting preset voltages to power supply
        PowerSupply.setVoltage_V(EffVHighStep_mV)

        #We wait for voltage to establish 
        time.sleep(1)
        SPIN_Comm.FlushSerialBuffer(STLINK)

        #For each current step we perform a duty cycle
        for i in range(0, (Settings.json_data["EffNumberOfIHighStep"]), 1):

            Settings.TestEfficiencyProgress+=1

            print("Iterating through Current set point:", (i+Settings.json_data["EffStepMinIHigh_mA"]), "\n")

            #Setting current to load
            CurrentSentToLoad_A = ((Settings.json_data["EffIHighStepArray_mA"][i])/(Settings.MilliToUnitConversionRatio))
            ActiveLoad.SetCurrent_A(ActiveLoadObj, Settings.ActiveLoadAddress, CurrentSentToLoad_A)
            #Performing duty cycle
            SPIN_Comm.DutySweep(STLINK, CSVPath, Settings.json_data["NumberOfStepInDutySweep"], DMMDict,\
                                 Settings.CoreConfigDict, Settings.json_data["NumberOfPointsPerDuty"])

        #Compute efficiency measure with TWIST measures
        OrganizeDataInCSV.ComputeTWISTEff(CSVPath)

        #Compute error of power between TWIST and DMM
        OrganizeDataInCSV.ComputeTWISTPowerErr(CSVPath)

        #Compute error of efficiency between TWIST and DMM
        OrganizeDataInCSV.ComputeTWISTEffErr(CSVPath)

        #Compute the average of measures and its related standard deviation
        OrganizeDataInCSV.AverageBlockAndStdDev(CSVPath, Settings.json_data["NumberOfPointsPerDuty"])

        # Plot.PlotHistoDistrib(CSVPath, "No", Settings.duty_step_Percent-1)

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

    PathListsAVGD = FileMngt.CreateListOfAveragedTestsResults(PathLists)

    # Plot the results
    Plot.PlotEff2D(PathListsAVGD, LowLeg, "No")
    Plot.PlotPowerError(PathListsAVGD, LowLeg, Settings.json_data["NumberOfPointsPerDuty"], "No")
    Plot.PlotEff3D(PathListsAVGD, LowLeg)
    Plot.PlotErr3D(PathListsAVGD, LowLeg, "Abs")
    Plot.PlotErr3D(PathListsAVGD, LowLeg, "Rel")
    
    Settings.TestEfficiencyProgress+=1

###################################################################
#                              main                               #
###################################################################
def main():
    debug = 0 #1 for debug mode, 0 for normal mode
    #In debug mode, test folder is named Debug
    #Also, leg efficiency is not requested and is by default on leg 1

    start_time=time.time()

    MeasureEfficiency()
    
    end_time=time.time()
    elapsed=end_time-start_time

    print("Elapsed:\n", elapsed)

###################################################################
#                          Entry point                            #
###################################################################
if __name__ == "__main__":

    main()
