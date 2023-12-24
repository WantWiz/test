import array, numpy as np
import serial.tools.list_ports
import json

###################################################################
#                       GetCOMObjectPORT                          #
# Desc : this function is intended to handle the issue of serial  #
# port randomly changing                                          #
# Input : COMObjectDesc (str) : the COM object description we     #
# want to get the COM Port                                        #
# Output : the COM Port of the input                              #
###################################################################
def GetCOMObjectPORT(COMObjectDesc):
    # Get a list of all available serial ports
    available_ports = serial.tools.list_ports.comports()

    # Loop through all available ports and look for the one that matches the input COM port name
    for port in available_ports:
        descWithPort = port.description
        descWithoutPort = descWithPort.split('(COM')[0].strip()
        if descWithoutPort == COMObjectDesc:
            # Return the matching port name
            return port.device
    
    # If no match was found, return None
    return None

TestCoefficientsProgress = 0
TestEfficiencyProgress = 0
TestAccuracyProgress = 0
TestHistogramProgress = 0

with open("json_DefaultParameters.json",'r') as f:
    json_data = json.load(f)

# number of parameters in the json
NumberOfNoneArrayParamInJson = sum(1 for value in json_data.values() if value != "")
ArrayIndexInJson = tuple(index for index, value in enumerate(json_data.values()) if value == "")

with open("JsonTestsHistory.json", "r") as f:
    JsonTestsHistory_data = json.load(f)

def refresh_JsonTestsHistory():
    with open("JsonTestsHistory.json", "r") as f:
        JsonTestsHistory_data = json.load(f)

# with open("jsontest.json",'r') as f:
#     body = json.load(f)
#     values_tup = tuple(body.values())
#     key_tup = tuple(body.keys())

# for k, v in zip(key_tup, values_tup):
#     k = v
#     breakpoint()
#     print(k,v)

#*****************************************************************
#*****************************************************************
#                      Generic parameters                        #
#*****************************************************************
#*****************************************************************

###################################################################
#                 Serial communication items                      #
###################################################################
#Active load serial comm parameters
ITE132CommPortDescWithoutPort = "Prolific USB-to-Serial Comm Port"
ActiveLoadCommPorttmp = GetCOMObjectPORT(ITE132CommPortDescWithoutPort)
ActiveLoadCommPort=ActiveLoadCommPorttmp
ActiveLoadbaudRate = 9600
ActiveLoadbytesize = 8
ActiveLoadparity = "N"
ActiveLoadstopbits = 2
ActiveLoadsTimeout = 2
ActiveLoadAddress  = 0 #Address of active load (default is 0)

#Power supply serial comm parameters
PSUCommPortDescWithoutPort = "PSI 9000 DT Series"
PSUCommPorttmp = "COM5" #GetCOMObjectPORT(PSUCommPortDescWithoutPort)
PSUCommPort=PSUCommPorttmp

#STlink serial comm parameters
STLINKCommPortDescWithoutPort = "STMicroelectronics STLink Virtual COM Port"
STLINKCommPort = "COM7" #GetCOMObjectPORT(STLINKCommPortDescWithoutPort)
STLINKbaudRate = 115200
STLINKbytesize = 8
STLINKparity ="N"
STLINKstopbits = 1
STLINKTimeout_s = 2

# ###################################################################
# #                 Active load safety values                       #
# ###################################################################
# LoadInternalSafetyCurrent_A = 10 # : Hardware current limitation of load
# LoadInternalSafetyPower_W = 180 # : Hardware power limitation of load

# ###################################################################
# #                      Duty step in duty sweep                    #
# ###################################################################
# NumberOfPointsPerDuty = 2 #Number of samples read per duty, same for DMM and SPIN
# NumberOfStepInDutySweep = 2 # The number of times we increase D for ONE Duty sweep. 
# # Example : if NumberOfUpSent = 10, the final duty cycle will be :
# # Final D =  starting_duty_cycle_Percent + NumberOfStepInDutySweep*duty_step_Percent
# # Final D = 5+5*10 = 50%
# # if NumberOfUpSent = 16, the final duty cycle will be 5*17 = 85%

# ###################################################################
# #                    core related variables                       #
# ###################################################################
# duty_step_Percent = 5 #Equal to duty_cycle_step core variable
# starting_duty_cycle_Percent = 5 #equal to starting_duty_cycle core variable :
# #corresponds to the duty set when r command is sent

CoreConfigDict = {
    "Duty Step Percent" : json_data["duty_step_Percent"],
    "Starting Duty" : json_data["starting_duty_cycle_Percent"]
}


###################################################################
#                    Calibration Coefficients                     #
###################################################################

CalibrationCoeffs = {
"gV1": "",
"oV1": "",
"r_sqV1": "", 
"gV2": "",
"oV2": "",
"r_sqV2": "", 
"gVH": "",
"oVH": "",
"r_sqVH": "", 
"gI1": "",
"oI1": "",
"r_sqI1": "",
"gI2": "",
"oI2": "",
"r_sqI2": "", 
"gIH": "",
"oIH": "",
"r_sqIH": "", 
}

#*****************************************************************
#*****************************************************************
#                     Efficiency related                         #
#*****************************************************************
#*****************************************************************

###################################################################
#           Current step number and step values                   #
###################################################################
#Current step definitions
#For every current step we run a DutySweep.
#Change step values with the CurrentStepValue_x_mA variable
#Change starting step with the StartCurrentStep variable. The total 
# current step will be equal to NumberOfCurrentStep variable

# StartCurrentStep = 0
# StopCurrentStep = 5

# NumberOfCurrentStep = ((StopCurrentStep-StartCurrentStep)+1) #The total number of current step

# CurrentStepValue_0_mA = 500
# CurrentStepValue_1_mA = 1500
# CurrentStepValue_2_mA = 2500
# CurrentStepValue_3_mA = 3500
# CurrentStepValue_4_mA = 4500
# CurrentStepValue_5_mA = 5500
# # CurrentStepValue_6_mA = 6500
# # CurrentStepValue_7_mA = 7500

# CurrentStepArray_mA = array.array('i',[CurrentStepValue_0_mA,CurrentStepValue_1_mA,\
#     CurrentStepValue_2_mA,CurrentStepValue_3_mA,CurrentStepValue_4_mA,\
#     CurrentStepValue_5_mA])

###################################################################
#                      Header of saved CSV                        #
###################################################################
SavedCSVHeader = ['Duty cycle (%)','DMM VHigh (mV)', 'DMM IHigh (mA)',\
'DMM VLow (mV)', 'DMM ILow (mA)', 'DMM POWER High (W)','DMM POWER Low (W)', 'DMM Efficiency (%)',\
'TWIST Duty Cycle (%)', 'TWIST VHigh (mV)', 'TWIST VLow1 (mV)', 'TWIST VLow2 (mV)', 'TWIST IHigh (mA)',\
'TWIST ILow1 (mA)', 'TWIST ILow2 (mA)']

###################################################################
#                 GPIB Instruments addresses                      #
###################################################################
IHighGPIBAddress = 'GPIB0::1::INSTR'
VHighGPIBAddress = 'GPIB0::2::INSTR'
VLowGPIBAddress = 'GPIB0::3::INSTR'
ILowGPIBAddress = 'GPIB0::4::INSTR'

###################################################################
#                       Conversion ratio                          #
###################################################################
PrecentToUnitConversionRatio = 100
MilliToUnitConversionRatio = 1000

###################################################################
#                       Hardware config                           #
###################################################################
shunt_value_in_mOhm = 10 #The value of the shunt for high and low side current measure

IHighShuntCorrectionFactor = 1.033
ILowShuntCorrectionFactor = 1.039

###################################################################
#                         DMM settings                            #
###################################################################
DMM_READING_INTERVAL_ms = 1 #ms, the interval between each sampling point for the average of DMM measure
Number_of_DMM_READ_AVG = 2 #Number of samples to compute the average of DMM measure

###################################################################
#              Delays for steady state reach                      #
###################################################################
TimeWaitedForSteadyStateReach_Reset_ms = 2000
TimeWaitedForSteadyStateReach_ms = 100

#*****************************************************************
#*****************************************************************
#                       Accuracy related                         #
#*****************************************************************
#*****************************************************************

###################################################################
#                           Accuracy Header                      #
###################################################################
AccVHighHeader = ['DMM VHigh (mV)', 'TWIST Duty Cycle', 'TWIST VHigh (mV)', 'TWIST VLow1 (mV)',\
'TWIST VLow2 (mV)', 'TWIST IHigh (mA)', 'TWIST ILow1 (mA)', 'TWIST ILow2 (mA)']

AccIHighHeader =  ['DMM IHigh (mA)', 'TWIST Duty Cycle', 'TWIST VHigh (mV)', 'TWIST VLow1 (mV)',\
'TWIST VLow2 (mV)', 'TWIST IHigh (mA)', 'TWIST ILow1 (mA)', 'TWIST ILow2 (mA)']

AccVLowHeader = ['DMM VLow (mV)', 'TWIST Duty Cycle', 'TWIST VHigh (mV)', 'TWIST VLow1 (mV)',\
'TWIST VLow2 (mV)', 'TWIST IHigh (mA)', 'TWIST ILow1 (mA)', 'TWIST ILow2 (mA)']

AccILowHeader = ['DMM ILow (mA)', 'TWIST Duty Cycle', 'TWIST VHigh (mV)', 'TWIST VLow1 (mV)',\
'TWIST VLow2 (mV)', 'TWIST IHigh (mA)', 'TWIST ILow1 (mA)', 'TWIST ILow2 (mA)']

AccHeaderDict = {
    "VHigh": AccVHighHeader,
    "IHigh": AccIHighHeader,
    "VLow": AccVLowHeader,
    "ILow": AccILowHeader,
}

###################################################################
#                           Histogram Header                      #
###################################################################
HistVHighHeader = ['DMM VHigh (mV)', 'TWIST Duty Cycle', 'TWIST VHigh (mV)', 'TWIST VLow1 (mV)',\
'TWIST VLow2 (mV)', 'TWIST IHigh (mA)', 'TWIST ILow1 (mA)', 'TWIST ILow2 (mA)']

HistIHighHeader =  ['DMM IHigh (mA)', 'TWIST Duty Cycle', 'TWIST VHigh (mV)', 'TWIST VLow1 (mV)',\
'TWIST VLow2 (mV)', 'TWIST IHigh (mA)', 'TWIST ILow1 (mA)', 'TWIST ILow2 (mA)']

HistVLowHeader = ['DMM VLow (mV)', 'TWIST Duty Cycle', 'TWIST VHigh (mV)', 'TWIST VLow1 (mV)',\
'TWIST VLow2 (mV)', 'TWIST IHigh (mA)', 'TWIST ILow1 (mA)', 'TWIST ILow2 (mA)']

HistILowHeader = ['DMM ILow (mA)', 'TWIST Duty Cycle', 'TWIST VHigh (mV)', 'TWIST VLow1 (mV)',\
'TWIST VLow2 (mV)', 'TWIST IHigh (mA)', 'TWIST ILow1 (mA)', 'TWIST ILow2 (mA)']

HistHeaderDict = {
    "VHigh": HistVHighHeader,
    "IHigh": HistIHighHeader,
    "VLow": HistVLowHeader,
    "ILow": HistILowHeader,
}

HistMeanStandardDeviationDict = {
    "VHigh (mV)" : {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "IHigh (mA)" : {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "VLow1 (mV)" : {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "VLow2 (mV)" : {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "ILow1 (mA)" : {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "ILow2 (mA)" : {
        "Mean" : "",
        "StandartDeviation" : "",
    },
}

# ###################################################################
# #                 Calibration working points                      #
# ###################################################################
# #VHigh
# AccVHighCalibrationDutyPercent = 50
# AccVHighCalibrationLowCurrent_mA = 1000

# #IHigh
# AccIHighCalibrationDuty_Percent = 50
# AccIHighCalibrationVHigh_mV = 48000

# #VLow
# AccVLowCalibrationLowCurrent_mA = 1000
# AccVLowCalibrationVHigh_mV = 96000

# #ILow
# AccILowCalibrationDuty_Percent = 50
# AccILowCalibrationVHigh_mV = 48000

# ###################################################################
# #               Number of step in VLow duty sweep                 #
# ###################################################################
# AccNumberOfStepInVLowDutySweep = 15 # The number of times we increase D for ONE Duty sweep. 
# # Example : if NumberOfUpSent = 10, the final duty cycle will be :
# # Final D =  starting_duty_cycle_Percent + NumberOfStepInDutySweep*duty_step_Percent
# # Final D = 5+5*10 = 50%
# # if NumberOfUpSent = 16, the final duty cycle will be 5*17 = 85%

# ###################################################################
# #             VHigh step number and step values                   #
# ###################################################################
# AccNumberOfVHighStep = 20

# AccStepMinVHigh_mV = 15000
# AccStepMaxVHigh_mV = 96000

# AccVHighStepArray_mV = np.linspace(json_data["AccStepMinVHigh_mV"], json_data["AccStepMaxVHigh_mV"], json_data["AccNumberOfVHighStep"])
# AccVHighStepArray_mV = [round(num, 0) for num in AccVHighStepArray_mV]

# ###################################################################
# #           IHigh step number and step values                   #
# ###################################################################
# AccIHighNumberOfCurrentStep = 20

# AccIHighStepMinCurrent_mA = 100
# AccIHighStepMaxCurrent_mA = 7500

# AccIHighCurrentStepArray_mA = np.linspace(json_data["AccIHighStepMinCurrent_mA"], json_data["AccIHighStepMaxCurrent_mA"], json_data["AccIHighNumberOfCurrentStep"])
# AccIHighCurrentStepArray_mA = [round(num, 0) for num in AccIHighCurrentStepArray_mA]

# ###################################################################
# #           ILow step number and step values                   #
# ###################################################################
# AccILowNumberOfCurrentStep = 20

# AccILowStepMinCurrent_mA = 100
# AccILowStepMaxCurrent_mA = 7500

# AccILowCurrentStepArray_mA = np.linspace(json_data["AccILowStepMinCurrent_mA"], json_data["AccILowStepMaxCurrent_mA"], json_data["AccILowNumberOfCurrentStep"])
# AccILowCurrentStepArray_mA = [round(num, 0) for num in AccILowCurrentStepArray_mA]


# #*****************************************************************
# #*****************************************************************
# #                     Coefficients related                       #
# #*****************************************************************
# #*****************************************************************

# ###################################################################
# #                          Sampling count                         #
# ###################################################################
# CoeffNumberOfTWISTMeas = 5

# ###################################################################
# #                          Working points                         #
# ###################################################################

# #VHigh
# CoeffVHighCalibrationDutyPercent = 50
# CoeffVHighCalibrationLowCurrent_mA = 1000

# #IHigh
# CoeffIHighCalibrationDuty_Percent = 50
# CoeffIHighCalibrationVHigh_mV = 48000

# #VLow
# CoeffVLowCalibrationLowCurrent_mA = 1000
# CoeffVLowCalibrationVHigh_mV = 96000

# #ILow
# CoeffILowCalibrationDuty_Percent = 50
# CoeffILowCalibrationVHigh_mV = 48000

###################################################################
#                           Headers                               #
###################################################################

CoeffHeaderVHigh = ['DMM VHigh (mV)', 'TWIST Duty Cycle', 'TWIST VHigh (quantum)', 'TWIST VLow1 (quantum)',\
    'TWIST VLow2 (quantum)', 'TWIST IHigh (quantum)', 'TWIST ILow1 (quantum)', 'TWIST ILow2 (quantum)']

CoeffHeaderIHigh = ['DMM IHigh (mA)', 'TWIST Duty Cycle', 'TWIST VHigh (quantum)', 'TWIST VLow1 (quantum)',\
    'TWIST VLow2 (quantum)', 'TWIST IHigh (quantum)', 'TWIST ILow1 (quantum)', 'TWIST ILow2 (quantum)']

CoeffHeaderVLow = ['DMM VLow (mV)', 'TWIST Duty Cycle', 'TWIST VHigh (quantum)', 'TWIST VLow1 (quantum)',\
    'TWIST VLow2 (quantum)', 'TWIST IHigh (quantum)', 'TWIST ILow1 (quantum)', 'TWIST ILow2 (quantum)']

CoeffHeaderILow = ['DMM ILow (mA)', 'TWIST Duty Cycle', 'TWIST VHigh (quantum)', 'TWIST VLow1 (quantum)',\
    'TWIST VLow2 (quantum)', 'TWIST IHigh (quantum)', 'TWIST ILow1 (quantum)', 'TWIST ILow2 (quantum)']


# ###################################################################
# #             VHigh step number and step values                   #
# ###################################################################
# CoeffStepMinVHigh_mV = 15000
# CoeffStepMaxVHigh_mV = 96000

# CoeffNumberOfVHighStep = 5

# CoeffVHighStepArray_mV = np.linspace(json_data["CoeffStepMinVHigh_mV"], json_data["CoeffStepMaxVHigh_mV"], json_data["CoeffNumberOfVHighStep"])
# CoeffVHighStepArray_mV = [round(num, 0) for num in CoeffVHighStepArray_mV]

# ###################################################################
# #           Current step number and step values                   #
# ###################################################################
# CoeffStepMinCurrent_mA = 100
# CoeffStepMaxCurrent_mA = 7500

# CoeffNumberOfCurrentStep = 5

# CoeffCurrentStepArray_mA = np.linspace(json_data["CoeffStepMinCurrent_mA"], json_data["CoeffStepMaxCurrent_mA"], json_data["CoeffNumberOfCurrentStep"])
# CoeffCurrentStepArray_mA = [round(num, 0) for num in CoeffCurrentStepArray_mA]

# ###################################################################
# #                      Duty step in duty sweep                    #
# ###################################################################
CoeffNumberOfStepInDutySweep = 5 # The number of times we increase D for ONE Duty sweep. 
# # Example : if NumberOfUpSent = 10, the final duty cycle will be :
# # Final D =  starting_duty_cycle_Percent + NumberOfStepInDutySweep*duty_step_Percent
# # Final D = 5+5*10 = 50%
# # if NumberOfUpSent = 16, the final duty cycle will be 5*17 = 85%

CoeffsHistoryMeanStandardDeviationDict = {
    "GV1": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "OV1": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "GV2": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "OV2": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "GVH": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "OVH": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "GI1": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "OI1": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "GI2": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "OI2": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "GIH": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "OIH": {
        "Mean" : "",
        "StandartDeviation" : "",
    }
}

HistoHistoryMeanStandardDeviationDictLeg1 = {
    "VHigh (mV)_Mean": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "VHigh (mV)_StandartDeviation": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "IHigh (mA)_Mean": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "IHigh (mA)_StandartDeviation": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "VLow1 (mV)_Mean": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "VLow1 (mV)_StandartDeviation": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "VLow2 (mV)_Mean": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "VLow2 (mV)_StandartDeviation": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "ILow1 (mA)_Mean": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "ILow1 (mA)_StandartDeviation": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "ILow2 (mA)_Mean": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "ILow2 (mA)_StandartDeviation": {
    "Mean" : "",
    "StandartDeviation" : "",
    }
}

HistoHistoryMeanStandardDeviationDictLeg2 = {
    "VHigh (mV)_Mean": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "VHigh (mV)_StandartDeviation": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "IHigh (mA)_Mean": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "IHigh (mA)_StandartDeviation": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "VLow1 (mV)_Mean": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "VLow1 (mV)_StandartDeviation": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "VLow2 (mV)_Mean": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "VLow2 (mV)_StandartDeviation": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "ILow1 (mA)_Mean": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "ILow1 (mA)_StandartDeviation": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "ILow2 (mA)_Mean": {
        "Mean" : "",
        "StandartDeviation" : "",
    },
    "ILow2 (mA)_StandartDeviation": {
    "Mean" : "",
    "StandartDeviation" : "",
    }
}