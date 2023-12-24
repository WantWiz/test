import os, SPIN_Comm, time, sys, serial

ScriptPath = os.path.dirname(os.path.abspath(__file__))
LibFolderName = "Libraries"

LibPath = os.path.join(ScriptPath, LibFolderName)
# caution: path[0] is reserved for script path (or '' in REPL)
# sys.path.insert(0, LibPath)
sys.path.insert(1, LibPath)

import MonitoringMeasures, Settings

###################################################################
#                    InitSerialObjectTimeout                      #
###################################################################
def InitSerialObjectTimeout(SerialObj, baudrate, bytesize, parity, stopbits, timeout_sec):
    SerialObj.baudrate = baudrate
    SerialObj.bytesize = bytesize
    SerialObj.parity = parity
    SerialObj.stopbits = stopbits
    SerialObj.timeout = timeout_sec

###################################################################
#                    InitSerialObjectNoTimeout                    #
###################################################################
def InitSerialObjectNoTimeout(SerialObj, baudrate, bytesize, parity, stopbits):
    SerialObj.baudrate = baudrate
    SerialObj.bytesize = bytesize
    SerialObj.parity = parity
    SerialObj.stopbits = stopbits

###################################################################
#                      GetDutyFromSerial                          #
###################################################################
def GetDutyFromSerial(SerialObj):

    SerialObj.flush() #flush
    OneSerialLine = SerialObj.readline() #read truncated line
    OneSerialLine = SerialObj.readline() #line should be full
    Formatted_One_Line = [float(y) for y in OneSerialLine.decode('utf-8')[:-1].split(':')]#mise en forme

    LastDuty=int(Formatted_One_Line[0]*100)
    return LastDuty

###################################################################
#                    FlushUntilExpectedDuty                       #
###################################################################
def FlushUntilExpectedDuty(SerialObj, ExpectedDuty_Percent):

    LastDuty = SPIN_Comm.GetDutyFromSerial(SerialObj)
    while(ExpectedDuty_Percent!=LastDuty):
        LastDuty = SPIN_Comm.GetDutyFromSerial(SerialObj)


###################################################################
#                      WriteWithHandshake                         #
###################################################################
def WriteWithHandshake(SerialObj, text):

    SerialObj.flushInput()#Flush input buffer
    time.sleep(0.1)
    #Building text to send
    text = text + '\r'
    #Sending
    SerialObj.write(text.encode())
    time.sleep(0.1)

    #Building expected echo
    expectedecho = text + '\n'

    #Reading one line, waiting for echo
    OneSerialLine = SerialObj.readline()
    echo = OneSerialLine.decode('utf-8')

    #If echo is not good, send \r until it is good
    while (echo != expectedecho):
        SerialObj.write(text.encode())
        OneSerialLine = SerialObj.readline()
        echo = OneSerialLine.decode('utf-8')

###################################################################
#                      SetTwistPowerMode                          #
###################################################################
def SetTwistPowerMode(SerialObj):

    SerialObj.write(b'p')

###################################################################
#                        FlushSerialBuffer                        #
###################################################################
def FlushSerialBuffer(SerialObj):

    SerialObj.flushInput()
    SerialObj.readline()#So it scraps the cropped line (if there is one)

###################################################################
#                    FlushSerialBufferInAndOut                    #
###################################################################
def FlushSerialBufferInAndOut(SerialObj):

    SerialObj.flushInput()
    SerialObj.flushOutput()

###################################################################
#                     SetTWISTDutyCycle                           #
###################################################################
def SetTWISTDutyCycle(SerialObj, DutyReset_per, DutyStep_per, DutyTarget_per):

    SerialObj.write(b'r')
    NumberOfup = int((DutyTarget_per - DutyReset_per)/DutyStep_per)

    for i in range(0, NumberOfup):
        SerialObj.write(b'u')
        print("Sending up")
        time.sleep(0.2)

###################################################################
#                        UpdateDutyStep                           #
###################################################################
def UpdateDutyStep(duty_step_percent):

    STLINK = serial.Serial(Settings.STLINKCommPort)

    SPIN_Comm.InitSerialObjectTimeout(STLINK, Settings.STLINKbaudRate, Settings.STLINKbytesize,\
    Settings.STLINKparity, Settings.STLINKstopbits, Settings.STLINKTimeout_s)
    
    #Entering duty step update value
    STLINK.write(b'x')
    time.sleep(1)


    duty_step_percent_str = str(duty_step_percent)

    string_sent = duty_step_percent_str + '\r\n'
    for char in string_sent:
        STLINK.write(char.encode())#"ascii"
        time.sleep(0.1)#Sleep 100ms between each car

        time.sleep(0.5)#Sleep after EOL car

    #Confirming
    STLINK.write(b'y')
    time.sleep(0.5)

###################################################################
#                       SetCoefficients                           #
###################################################################
def SetCoefficients(SerialObj, CoeffDict):

    #Order of gains and offsets to be sent: 
    #V1Low, V2Low, VHigh, I1Low, I2Low, IHigh

    #Entering coefficient update mode
    SerialObj.write(b'k')
    time.sleep(1)

    #Loop sending gains
    for key, value in CoeffDict.items():#Iterates keys of dictionnary
        
        Settings.TestCoefficientsProgress+=1

        if key.startswith("g"):
            print(key + " applied is : " + str(value))

            mystring = str(value) + '\r\n'
            for char in mystring:
                SerialObj.write(char.encode())#"ascii"
                time.sleep(0.1)#Sleep 100ms between each car

            time.sleep(0.5)#Sleep after EOL car

            #Confirming
            SerialObj.write(b'y')
            time.sleep(0.5)

    #Loop sending offsets
    for key, value in CoeffDict.items():#Iterates keys of dictionnary

        if key.startswith("o"):
            print(key + " applied is : " + str(value))

            mystring = str(value) + '\r\n'
            for char in mystring:
                SerialObj.write(char.encode())#"ascii"
                time.sleep(0.1)#Sleep 100ms between each car

            time.sleep(0.5)#Sleep after EOL car

            #Confirming
            SerialObj.write(b'y')
            time.sleep(0.5)

    time.sleep(1)#Wait before flushing input to make sure all 
    #data are arrived in the buffer
    SerialObj.flushInput()#Flushing input buffer
    print("Coefficients updated !")

###################################################################
#                           InitDutySweep                         #
###################################################################
def InitDutySweep(SerialObj):

    SerialObj.write(b'r')
    time.sleep(2)

    SerialObj.write(b'p')
    time.sleep(2)#Steady state reach delay

###################################################################
#                           ExitDutySweep                         #
###################################################################
def ExitDutySweep(SerialObj):
    SerialObj.write(b'r')

###################################################################
#                          DutySweep                             #
###################################################################
def DutySweep(SerialObj, PathFileToSave, StepsInSweep, DMMDict, CoreConfigDict, NumberOfPointsPerDuty):

    Duty_Percent = CoreConfigDict["Starting Duty"]

    InitDutySweep(SerialObj)

    SPIN_Comm.FlushUntilExpectedDuty(SerialObj, CoreConfigDict["Starting Duty"])

    for i in range(0, NumberOfPointsPerDuty, 1):
        print("Reading: ", i)
        MonitoringMeasures.GetDMMPowerSerialMeasAndSaveItInCSV(SerialObj, PathFileToSave, Duty_Percent, DMMDict)

    for i in range(0, StepsInSweep, 1):
        print("Sending u :", (i))

        SerialObj.write(b'u')
        time.sleep(1)#Time for set point to establish

        Duty_Percent+=CoreConfigDict["Duty Step Percent"]
        SPIN_Comm.FlushUntilExpectedDuty(SerialObj, Duty_Percent)

        for i in range(0, NumberOfPointsPerDuty, 1):
            print("Reading: ", i)
            MonitoringMeasures.GetDMMPowerSerialMeasAndSaveItInCSV(SerialObj, PathFileToSave, Duty_Percent, DMMDict)

    ExitDutySweep(SerialObj)