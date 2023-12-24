import csv, os, sys

ScriptPath = os.path.dirname(os.path.abspath(__file__))
LibFolderName = "Libraries"

LibPath = os.path.join(ScriptPath, LibFolderName)
# caution: path[0] is reserved for script path (or '' in REPL)
# sys.path.insert(0, LibPath)
sys.path.insert(1, LibPath)

import Settings, Power

###################################################################
#                       GetDMMMeasurements                        #
###################################################################
def GetDMMMeasurements(DMMDict):

    #Initialize array 
    Dataset = [0]*4 

    Vshunt_IHigh_mV=DMMDict["IHigh"].getAveragedVoltage_mV((Settings.Number_of_DMM_READ_AVG),(Settings.DMM_READING_INTERVAL_ms))#voltage across input shunt
    VHigh_mV=DMMDict["VHigh"].getAveragedVoltage_mV((Settings.Number_of_DMM_READ_AVG),(Settings.DMM_READING_INTERVAL_ms))#input voltage
    VLow_mV=DMMDict["VLow"].getAveragedVoltage_mV((Settings.Number_of_DMM_READ_AVG),(Settings.DMM_READING_INTERVAL_ms))#output voltage
    Vshunt_ILow_mV=DMMDict["ILow"].getAveragedVoltage_mV((Settings.Number_of_DMM_READ_AVG),(Settings.DMM_READING_INTERVAL_ms))#voltage across output shunt

    #Compute current from shunt 
    IHigh_mA=Power.ShuntVoltage_mVToCurr_mA(Vshunt_IHigh_mV,(Settings.shunt_value_in_mOhm),Settings.IHighShuntCorrectionFactor)
    ILow_mA=Power.ShuntVoltage_mVToCurr_mA(Vshunt_ILow_mV,(Settings.shunt_value_in_mOhm),Settings.ILowShuntCorrectionFactor)

    Dataset[0]=round(VHigh_mV)
    Dataset[1]=round(IHigh_mA)
    Dataset[2]=round(VLow_mV)
    Dataset[3]=round(ILow_mA)

    return Dataset

###################################################################
#             GetDMMSingleMeasSerialMeasAndSaveItInCSV            #
###################################################################
def GetDMMSingleMeasSerialMeasAndSaveItInCSV(Choice, STLINK, CSVPATH, DMMDict):

    #Initialize array 
    DataDMM = [0]*1

    Vshunt_IHigh_mV=DMMDict["IHigh"].getAveragedVoltage_mV((Settings.Number_of_DMM_READ_AVG),(Settings.DMM_READING_INTERVAL_ms))#voltage across input shunt
    VHigh_mV=DMMDict["VHigh"].getAveragedVoltage_mV((Settings.Number_of_DMM_READ_AVG),(Settings.DMM_READING_INTERVAL_ms))#input voltage
    VLow_mV=DMMDict["VLow"].getAveragedVoltage_mV((Settings.Number_of_DMM_READ_AVG),(Settings.DMM_READING_INTERVAL_ms))#output voltage
    Vshunt_ILow_mV=DMMDict["ILow"].getAveragedVoltage_mV((Settings.Number_of_DMM_READ_AVG),(Settings.DMM_READING_INTERVAL_ms))#voltage across output shunt

    #Compute current from shunt 
    IHigh_mA=Power.ShuntVoltage_mVToCurr_mA(Vshunt_IHigh_mV,(Settings.shunt_value_in_mOhm),Settings.IHighShuntCorrectionFactor)
    ILow_mA=Power.ShuntVoltage_mVToCurr_mA(Vshunt_ILow_mV,(Settings.shunt_value_in_mOhm),Settings.ILowShuntCorrectionFactor)

    VHigh_mV=round(VHigh_mV)
    IHigh_mA=round(IHigh_mA)
    VLow_mV=round(VLow_mV)
    ILow_mA=round(ILow_mA)

    if(Choice == "VHigh"):
        DataDMM[0] = VHigh_mV
    elif(Choice == "IHigh"):
        DataDMM[0] = IHigh_mA
    elif(Choice == "VLow"):
        DataDMM[0] = VLow_mV
    elif(Choice == "ILow"):
        DataDMM[0] = ILow_mA
    
    #Getting serial line informations
    OneSerialLine = STLINK.readline()
    print(OneSerialLine)
    Formatted_One_Line = [float(y) for y in OneSerialLine.decode('utf-8')[:-1].split(':') if y != '']#mise en forme
    if Formatted_One_Line != []:
        Formatted_One_Line[0] = Formatted_One_Line[0]*100


    #Building the csv line 
    CSVLine =  DataDMM + Formatted_One_Line

    #Write line in csv file 
    with open(CSVPATH, 'a', newline='', encoding='UTF8') as file:
        writer = csv.writer(file, delimiter= '\t')
        writer.writerow(CSVLine)

###################################################################
#                   GetDMMSerialMeasAndSaveItInCSV                #
###################################################################
def GetDMMSerialMeasAndSaveItInCSV(STLINK, CSVPATH, DMMDict):

    #initialize CSV line (each index will be a csv column)
    CSVLine = [0]*1

    #Getting DMM measures
    DataDMM = GetDMMMeasurements(DMMDict)
    
    #Getting serial line informations
    OneSerialLine = STLINK.readline()
    print(OneSerialLine)
    Formatted_One_Line = [float(y) for y in OneSerialLine.decode('utf-8')[:-1].split(':') if y != '']#mise en forme
    if Formatted_One_Line != []:
        Formatted_One_Line[0] = Formatted_One_Line[0]*100

    #Building the csv line 
    CSVLine = CSVLine + DataDMM + Formatted_One_Line

    #Write line in csv file 
    with open(CSVPATH, 'a', newline='', encoding='UTF8') as file:
        writer = csv.writer(file, delimiter= '\t')
        writer.writerow(CSVLine)

###################################################################
#               GetDMMPowerSerialMeasAndSaveItInCSV               #
###################################################################
def GetDMMPowerSerialMeasAndSaveItInCSV(STLINK, CSVPATH, Duty, DMMDict):

    #initialize CSV line (each index will be a csv column)
    CSVLine = [0]*1
    CSVLine[0] = Duty

    #initialize power array
    PowerList = [0]*3

    #Getting DMM measures
    DataDMM = GetDMMMeasurements(DMMDict)

    #Computing PHigh, PLow, efficiency and returning it
    PowerList=Power.ComputePowerResults(DataDMM)
    
    #Getting serial line informations
    OneSerialLine = STLINK.readline()
    print(OneSerialLine)
    Formatted_One_Line = [float(y) for y in OneSerialLine.decode('utf-8')[:-1].split(':') if y != '']#mise en forme
    print(Formatted_One_Line)
    if Formatted_One_Line != []:
        Formatted_One_Line[0] = Formatted_One_Line[0]*100

    #Building the csv line 
    CSVLine = CSVLine + DataDMM + PowerList + Formatted_One_Line

    #Write line in csv file 
    with open(CSVPATH, 'a', newline='', encoding='UTF8') as file:
        writer = csv.writer(file, delimiter= '\t')
        writer.writerow(CSVLine)