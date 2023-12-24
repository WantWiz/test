import os, csv, serial, pyvisa, time, sys
import numpy as np
import pandas as pd
import shutil

# TestName ="TestCoef1"
#Importing libraries in libraries folder
ScriptPath = os.path.dirname(os.path.abspath(__file__))
LibFolderName = "Libraries"
LibPath = os.path.join(ScriptPath, LibFolderName)
# caution: path[0] is reserved for script path (or '' in REPL)
# sys.path.insert(0, LibPath)
sys.path.insert(1, LibPath)

import Settings, EAPSI9750, K2000, bk8500, ActiveLoad
import FileMngt, SPIN_Comm, Power

#Dictionnary of coefficients and associated r_sq (default values)
CoeffDict = {
"gV1": 1,
"oV1": 0,
"r_sqV1": 0, 
"gV2": 1,
"oV2": 0,
"r_sqV2": 0, 
"gVH": 1,
"oVH": 0,
"r_sqVH": 0, 
"gI1": 1,
"oI1": 0,
"r_sqI1": 0,
"gI2": 1,
"oI2": 0,
"r_sqI2": 0, 
"gIH": 1,
"oIH": 0,
"r_sqIH": 0, 
}

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
#                     SaveCalibrationCoeff                        #
###################################################################
def SaveCalibrationCoeff(CoeffsCSVPath, BoardSN, CoeffDict):

    with open(CoeffsCSVPath , 'a', newline='', encoding='UTF8') as file:

        writer = csv.writer(file, delimiter='\t')

        # Append a row with the specified values and save them in csv
        writer.writerow([BoardSN] + list(CoeffDict.values()))

###################################################################
#                          SaveHeader                             #
###################################################################
def SaveHeader(Choice, FilePath):

    HeaderVHigh = Settings.CoeffHeaderVHigh
    HeaderIHigh = Settings.CoeffHeaderIHigh
    HeaderVLow = Settings.CoeffHeaderVLow
    HeaderILow = Settings.CoeffHeaderILow

    if(Choice == "VHigh"):
        Header = HeaderVHigh
    elif(Choice == "IHigh"):
        Header = HeaderIHigh
    elif(Choice == "VLow"):
        Header = HeaderVLow
    elif(Choice == "ILow"):
        Header = HeaderILow

    with open(FilePath, 'w', newline='', encoding='UTF8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(Header)

##################################################################
#                           InitTest                             #
##################################################################
def InitTest(TestFolder, Choice, Leg, STLINK, ActiveLoadObj, PowerSupply):
    
    if(Choice == "VHigh" or Choice == "IHigh"):
        FilePath = TestFolder + '/' + Choice + '.csv'

    elif(Choice == "VLow" or Choice == "ILow"):
        FilePath = TestFolder + '/' + Choice + str(Leg) + '.csv'

    SaveHeader(Choice, FilePath)

    SetCalibrationWorkingPoints(STLINK, ActiveLoadObj, PowerSupply, Choice)

    return FilePath

##################################################################
#                 ComputeCalibrationCoeff                        #
##################################################################
def ComputeCalibrationCoeff(Choice, FilePath, LowLeg):

    df = pd.read_csv(FilePath, delimiter='\t')

    if(Choice == "VHigh"):
        x_mV = df["DMM VHigh (mV)"]
        y_quantum = df["TWIST VHigh (quantum)"]

    elif(Choice == "IHigh"):
        x_mV = df["DMM IHigh (mA)"]
        y_quantum = df["TWIST IHigh (quantum)"]

    elif(Choice == "VLow"):
        x_mV = df["DMM VLow (mV)"]
        if(LowLeg=="1"): 
            y_quantum = df["TWIST VLow1 (quantum)"]
        elif(LowLeg=="2"): 
            y_quantum = df["TWIST VLow2 (quantum)"]

    elif(Choice == "ILow"):
        x_mV = df["DMM ILow (mA)"]
        if(LowLeg=="1"): 
            y_quantum = df["TWIST ILow1 (quantum)"]
        elif(LowLeg=="2"): 
            y_quantum = df["TWIST ILow2 (quantum)"]

    tmpa, tmpb = np.polyfit(x_mV, y_quantum, 1)

    #For explanations see https://tinyurl.com/mvhhv2sm
    a=round(1/tmpa,3)
    b=round(-tmpb/tmpa, 0)

    # calculate the R² value of the regression
    y_pred = tmpa * x_mV + tmpb
    ss_res = np.sum((y_quantum - y_pred) ** 2)
    ss_tot = np.sum((y_quantum - np.mean(y_quantum)) ** 2)
    r_squared = round((1 - (ss_res / ss_tot)), 3)
    return a, b, r_squared

###################################################################
#                 ReadOneDMMAndSerialLineAndSaveIt                #
###################################################################
def ReadOneDMMAndSerialLineAndSaveIt(STLINK, Res, FilePath, Instance):

    print("Reading line: ", Instance)
    Dataset = [0]*1
    DMMMMeas_mV = Res.getAveragedVoltage_mV((Settings.Number_of_DMM_READ_AVG), (Settings.DMM_READING_INTERVAL_ms))

    if(Res == ILow):
        Dataset[0] = Power.ShuntVoltage_mVToCurr_mA(DMMMMeas_mV, Settings.shunt_value_in_mOhm,\
            Settings.ILowShuntCorrectionFactor)

    elif(Res == IHigh):
        Dataset[0] = Power.ShuntVoltage_mVToCurr_mA(DMMMMeas_mV, Settings.shunt_value_in_mOhm,\
            Settings.IHighShuntCorrectionFactor)

    else:#VHigh or VLow
        DMMMMeas_mV = round(DMMMMeas_mV, 0)
        Dataset[0] = DMMMMeas_mV

    OneSerialLine = STLINK.readline()
    Formatted_One_Line = [float(y) for y in OneSerialLine.decode('utf-8')[:-1].split(':') if y != '']#mise en forme
    Dataset = Dataset + Formatted_One_Line

    with open(FilePath, 'a', newline='', encoding='UTF8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(Dataset)

###################################################################
#                          GetVHighMeas                           #
###################################################################
def GetVHighMeas(FilePath, PowerSupply, STLINK):
    print("****Starting VHigh calibration****")

    for i in range(0,(Settings.json_data["CoeffNumberOfVHighStep"]),1):#for(x,y,z) number of iteration = y-x. z = step size (default = 1)
        
        Settings.TestCoefficientsProgress+=1
        
        print("\n ***VHigh step number : ", i)

        VHighStep_mV = Settings.json_data["CoeffVHighStepArray_mV"][i]
        PowerSupply.setVoltage_mV(VHighStep_mV)
        SPIN_Comm.FlushSerialBuffer(STLINK)

        for i in range(1,(Settings.json_data["CoeffNumberOfTWISTMeas"]+1),1):
            ReadOneDMMAndSerialLineAndSaveIt(STLINK, VHigh, FilePath, i)

###################################################################
#                            Duty_Sweep                           #
###################################################################
def Duty_Sweep(FilePath, STLINK):

    #Setting duty to reset value and enabling power
    STLINK.write(b'r')
    time.sleep(2)
    STLINK.write(b'p')
    SPIN_Comm.FlushSerialBuffer(STLINK)

    #Sweeping
    for i in range(0, (Settings.CoeffNumberOfStepInDutySweep+1)):
        
        Settings.TestCoefficientsProgress+=1

        for i in range(1,(Settings.json_data["CoeffNumberOfTWISTMeas"]+1),1):
            ReadOneDMMAndSerialLineAndSaveIt(STLINK, VLow, FilePath, i)

        print("Sending u :", (i))
        STLINK.write(b'u')
        time.sleep(0.100)#We wait for set point to establish
        SPIN_Comm.FlushSerialBuffer(STLINK)

    STLINK.write(b'r')#set duty cycle to DT min (defined in SPIN firmware)

###################################################################
#                          GetVLowMeas                             #
###################################################################
def GetVLowMeas(FilePath, STLINK):

    print("****Starting VLow calibration****")

    Duty_Sweep(FilePath, STLINK)

###################################################################
#                          GetIHighMeas                           #
###################################################################
def GetIHighMeas(FilePath, STLINK, ActiveLoadObj):
    
    print("****Starting IHigh calibration****")

    for i in range(0,(Settings.json_data["CoeffNumberOfCurrentStep"]),1):#for(x,y,z) number of iteration = y-x. z = step size (default = 1)

        Settings.TestCoefficientsProgress+=1

        print("\n ***Current step number : ", i)
        CurrentSentToLoad_A = ((Settings.json_data["CoeffCurrentStepArray_mA"][i])/(Settings.MilliToUnitConversionRatio))
        ActiveLoad.SetCurrent_A(ActiveLoadObj, Settings.ActiveLoadAddress, CurrentSentToLoad_A)

        SPIN_Comm.FlushSerialBuffer(STLINK)

        for i in range(1,(Settings.json_data["CoeffNumberOfTWISTMeas"]+1),1):
            ReadOneDMMAndSerialLineAndSaveIt(STLINK, IHigh, FilePath, i)

###################################################################
#                          GetILowMeas                            #
###################################################################
def GetILowMeas(FilePath, STLINK, ActiveLoadObj):
    
    print("****Starting ILow calibration****")

    for i in range(0,(Settings.json_data["CoeffNumberOfCurrentStep"]),1):#for(x,y,z) number of iteration = y-x. z = step size (default = 1)

        Settings.TestCoefficientsProgress+=1

        print("\n ***Current step number : ", i)
    
        CurrentSentToLoad_A = ((Settings.json_data["CoeffCurrentStepArray_mA"][i])/(Settings.MilliToUnitConversionRatio))
        ActiveLoad.SetCurrent_A(ActiveLoadObj, Settings.ActiveLoadAddress, CurrentSentToLoad_A)
        SPIN_Comm.FlushSerialBuffer(STLINK)

        for i in range(1,(Settings.json_data["CoeffNumberOfTWISTMeas"]+1),1):
            ReadOneDMMAndSerialLineAndSaveIt(STLINK, ILow, FilePath, i)

###################################################################
#                  SetCalibrationWorkingPoints                    #
###################################################################
def SetCalibrationWorkingPoints(STLINK, ActiveLoadObj, PowerSupply, Choice):

    if(Choice == "VHigh"):
        SPIN_Comm.SetTWISTDutyCycle(STLINK, Settings.json_data["starting_duty_cycle_Percent"],\
            Settings.json_data["duty_step_Percent"], Settings.json_data["CoeffVHighCalibrationDutyPercent"])
        
        CurrentSentToLoad_A = ((Settings.json_data["CoeffVHighCalibrationLowCurrent_mA"])/(Settings.MilliToUnitConversionRatio))
        ActiveLoad.SetCurrent_A(ActiveLoadObj, Settings.ActiveLoadAddress, CurrentSentToLoad_A)

    elif(Choice == "IHigh"):
        SPIN_Comm.SetTWISTDutyCycle(STLINK, Settings.json_data["starting_duty_cycle_Percent"],\
            Settings.json_data["duty_step_Percent"], Settings.json_data["CoeffIHighCalibrationDuty_Percent"])
        
        PowerSupply.setVoltage_mV(Settings.json_data["CoeffIHighCalibrationVHigh_mV"])

    elif(Choice == "VLow"):
        CurrentSentToLoad_A = ((Settings.json_data["CoeffVLowCalibrationLowCurrent_mA"])/(Settings.MilliToUnitConversionRatio))
        ActiveLoad.SetCurrent_A(ActiveLoadObj, Settings.ActiveLoadAddress, CurrentSentToLoad_A)

        PowerSupply.setVoltage_mV(Settings.json_data["CoeffVLowCalibrationVHigh_mV"])

    elif(Choice == "ILow"):
        SPIN_Comm.SetTWISTDutyCycle(STLINK, Settings.json_data["starting_duty_cycle_Percent"],\
            Settings.json_data["duty_step_Percent"], Settings.json_data["CoeffILowCalibrationDuty_Percent"])
        
        PowerSupply.setVoltage_mV(Settings.json_data["CoeffILowCalibrationVHigh_mV"])

    #Setting board in power mode
    STLINK.write(b'p')
    time.sleep((Settings.TimeWaitedForSteadyStateReach_Reset_ms)/1000)#Steady state reach delay

##################################################################
#                        GetCoefficients                         #
##################################################################
def GetCoefficients(TestName, BoardSN, LowLeg):

    Settings.TestCoefficientsProgress+=1

    global IHigh, VHigh, VLow, ILow

    #Connect INSTRUMENTS
    ResourceManager = pyvisa.ResourceManager()
    IHigh = K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.IHighGPIBAddress))
    VHigh = K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.VHighGPIBAddress))
    VLow = K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.VLowGPIBAddress))
    ILow = K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.ILowGPIBAddress))
    PowerSupply = EAPSI9750.EAPSI9750(ResourceManager.open_resource(Settings.PSUCommPort))
    STLINK = serial.Serial(Settings.STLINKCommPort)
    ActiveLoadObj = serial.Serial(Settings.ActiveLoadCommPort)

        #Dictionnary of DMM
    DMMDict =	{
    "IHigh": IHigh,
    "VHigh": VHigh,
    "VLow": VLow,
    "ILow": ILow,
    }

    #Init serial objects
    SPIN_Comm.InitSerialObjectTimeout(STLINK, Settings.STLINKbaudRate, Settings.STLINKbytesize,\
        Settings.STLINKparity, Settings.STLINKstopbits, Settings.STLINKTimeout_s)
    ActiveLoad.Init(ActiveLoadObj, Settings.ActiveLoadbaudRate, Settings.ActiveLoadparity,\
        Settings.ActiveLoadsTimeout)

    #If we are in debug, don't request test infos (time saving)
    # if(debug == 1):
    #     BoardSN = "Debug"
    #     LowLeg = "1"
    # elif(debug == 0):
    #     BoardSN = input("Board serial number : \n")
    #     LowLeg = input("Side for Low voltage and current measure (1/2): \n")

    # Create subfolder of test name  "Output_Coefficients" folder at root of script
    Dir = os.path.dirname(os.path.abspath(__file__))
    Dir = os.path.join(Dir, "Results")
    DirHistory = os.path.join(Dir, "Coeffs_Results_History")
    Dir = os.path.join(Dir, TestName)
    TestFolder = FileMngt.CreateSubfolder(Dir, "Output_Coefficients")

    #Setting path for Coefficients.csv file
    CoeffsCSVPathTest = TestFolder + '/' + 'Coeffs' + '_' + TestName + '.csv'
    CoeffsCSVPathTestHistory = DirHistory + '/' + 'Coeffs.csv'

    #Initialize Power supply
    PowerSupply.init()

    #Set active load safety settings
    ActiveLoad.SetSafetySettings(ActiveLoadObj, Settings.ActiveLoadAddress,\
    Settings.json_data["LoadInternalSafetyCurrent_A"], Settings.json_data["LoadInternalSafetyPower_W"])

    #Setting coefficients to gain = 1 and offset = 0 for proper calibration
    SPIN_Comm.SetCoefficients(STLINK, CoeffDict)

    #Array of parameter coefficient to be looped through
    ChoiceTab = ["VHigh", "IHigh", "VLow", "ILow"]
    for Choice in ChoiceTab:

        FilePath = InitTest(TestFolder, Choice, LowLeg, STLINK, ActiveLoadObj, PowerSupply)
        if(Choice == "VHigh"):
            GetVHighMeas(FilePath, PowerSupply, STLINK)#Getting data to compute a, b and r²
            a, b, rsq = ComputeCalibrationCoeff(Choice, FilePath, str(LowLeg)) #computing a, b and r²

            #storing a, b and r² into the coefficients dictionnary
            CoeffDict["gVH"] = a
            CoeffDict["oVH"] = b
            CoeffDict["r_sqVH"] = rsq

        elif(Choice == "IHigh"):
            GetIHighMeas(FilePath, STLINK, ActiveLoadObj)#Getting data to compute a, b and r²
            a, b, rsq = ComputeCalibrationCoeff(Choice, FilePath, str(LowLeg)) #computing a, b and r²

            #storing a, b and r² into the coefficients dictionnary
            CoeffDict["gIH"] = a
            CoeffDict["oIH"] = b
            CoeffDict["r_sqIH"] = rsq

        elif(Choice == "VLow"):
            GetVLowMeas(FilePath, STLINK)#Getting data to compute a, b and r²
            a, b, rsq = ComputeCalibrationCoeff(Choice, FilePath, str(LowLeg)) #computing a, b and r²

            #storing a, b and r² into the coefficients dictionnary
            if(int(LowLeg) == 1):
                CoeffDict["gV1"] = a
                CoeffDict["oV1"] = b
                CoeffDict["r_sqV1"] = rsq

            elif(int(LowLeg) == 2):
                CoeffDict["gV2"] = a
                CoeffDict["oV2"] = b
                CoeffDict["r_sqV2"] = rsq

        elif(Choice == "ILow"):
            GetILowMeas(FilePath, STLINK, ActiveLoadObj)#Getting data to compute a, b and r²
            a, b, rsq = ComputeCalibrationCoeff(Choice, FilePath, str(LowLeg)) #computing a, b and r²

            #storing a, b and r² into the coefficients dictionnary
            if(int(LowLeg) == 1):
                CoeffDict["gI1"] = a
                CoeffDict["oI1"] = b
                CoeffDict["r_sqI1"] = rsq

            elif(int(LowLeg) == 2):
                CoeffDict["gI2"] = a
                CoeffDict["oI2"] = b
                CoeffDict["r_sqI2"] = rsq
  
    columns = ["Board SN", "GV1", "OV1", "R²_V1", "GV2", "OV2", "R²_V2",
            "GVH", "OVH", "R²VH", "GI1", "OI1", "R²_I1",
            "GI2", "OI2", "R²_I2", "GIH", "OIH", "R²_IH"]

    with open(CoeffsCSVPathTest, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(columns)

    SaveCalibrationCoeff(CoeffsCSVPathTest, BoardSN, CoeffDict)#saving coefficients in Coeffs_TestName_LEG[1,2].csv
    SaveCalibrationCoeff(CoeffsCSVPathTestHistory, BoardSN, CoeffDict)

    PowerSupply.exit()

    #Disabling load remote control and set current to 0
    bk8500.enable_input(ActiveLoadObj, Settings.ActiveLoadAddress, False)
    bk8500.set_current(ActiveLoadObj, Settings.ActiveLoadAddress, 0)
    bk8500.set_remote(ActiveLoadObj, Settings.ActiveLoadAddress, False)

    #Setting TWIST in idle and reset duty for the exit of the test
    STLINK.write(b'i')
    STLINK.write(b'r')
    STLINK.close()

    Settings.TestCoefficientsProgress+=1
    
###################################################################
#                              main                               #
###################################################################
def main():

    debug = 0 #0 for normal mode, 1 for debug mode

    start_time=time.time()

    GetCoefficients(TestName, BoardSN, LowLeg)
    
    end_time=time.time()
    elapsed=end_time-start_time

    print("Elapsed:\n", elapsed)

###################################################################
#                          Entry point                            #
###################################################################
if __name__ == "__main__":

    main()