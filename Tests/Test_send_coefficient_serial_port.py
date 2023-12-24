import os, serial, sys, time, random

#Importing libraries from libraries folder
ScriptPath = os.path.dirname(os.path.abspath(__file__))
LibFolderName = "Libraries"
LibPath = os.path.join(ScriptPath, LibFolderName)

sys.path.insert(1, LibPath)

import SPIN_Comm

###################################################################
#                      ToggleNoHandshakeGetChar                   #
###################################################################
def ToggleNoHandshakeGetChar():
    while(1):

        STLINK.write('i'.encode("utf-8"))
        STLINK.flush()
        out_waiting_int = STLINK.out_waiting
        print(f"idle sent, {out_waiting_int=} \n")
        time.sleep(1)

        STLINK.write('p'.encode("utf-8"))
        STLINK.flush()
        out_waiting_int = STLINK.out_waiting
        print(f"power sent, {out_waiting_int=} \n")
        time.sleep(1)

###################################################################
#                        ToggleNoHandshake                        #
###################################################################
def ToggleNoHandshake():
    while(1):
        
        # STLINK.write(bytes(b'i\r\n'))
        STLINK.write('i'.encode("ascii"))
        print(f"idle sent \n")
        time.sleep(0.5)

        # STLINK.write(bytes(b'p\r\n'))
        STLINK.write('p'.encode("ascii"))
        print(f"power sent \n")
        time.sleep(0.5)

###################################################################
#                        ToggleHandshake                          #
###################################################################
def ToggleHandshake():

    while(1):
    
        text = 'i'
        SPIN_Comm.WriteWithHandshake(STLINK, text)
        print("idle sent")
        time.sleep(1)

        text = 'p'
        SPIN_Comm.WriteWithHandshake(STLINK, text)
        print("power sent")
        time.sleep(1)

        text = 'k'
        SPIN_Comm.WriteWithHandshake(STLINK, text)
        print("power sent")
        time.sleep(1)

###################################################################
#                        ReadSerialPort                           #
###################################################################
def EndlesslyMonitorSerialPort(SerialObj):

    #Flush crap to avoid error
    STLINK.flushInput()
    SerialObj.readline()

    while(1):#Endlessly read and print serial port
        OneSerialLine = SerialObj.readline()
        Formatted_One_Line = [float(y) for y in OneSerialLine.decode('utf-8')[:-1].split(':')]#mise en forme
        print(Formatted_One_Line)
        print("\n")

###################################################################
#                          Entry point                            #
###################################################################
if __name__ == "__main__":

    #Dictionnary of coefficients and associated r_sq (default values)
    CoeffDict = {
    "gVH": 1,
    "oVH": 100,
    "gV1": 1,
    "oV1": 200,
    "gV2": 1,
    "oV2": 300,
    "gIH": 1,
    "oIH": 400,
    "gI1": 1,
    "oI1": 500,
    "gI2": 1,
    "oI2": 600,
    }

    #Tab of coefficients from the dict (expected SetCoefficients arguments)
    gains = {k:v for k,v in CoeffDict.items() if k.startswith('g')}
    offsets = {k:v for k,v in CoeffDict.items() if k.startswith('o')}

    # STLINK = serial.serial_for_url("COM10", baudrate=115200, parity='N', bytesize=8, stopbits=1,\
    #         xonxoff=False, rtscts=False, dsrdtr=False, inter_byte_timeout=None, exclusive=None, do_not_open=True)
    # STLINK.open()

    STLINK = serial.Serial(port="COM28", baudrate=115200, parity='N', bytesize=8, stopbits=1,\
            xonxoff=False, rtscts=False, dsrdtr=False, inter_byte_timeout=None, exclusive=None)
    
    # time.sleep(5)

    # ToggleNoHandshakeGetChar()
    # ToggleNoHandshake()
    # ToggleHandshake()
    SPIN_Comm.SetCoefficients(STLINK, CoeffDict)

    while(STLINK.in_waiting>1):#Endlessly read and print serial port
        OneSerialLine = STLINK.readline().decode("ascii")
        print(OneSerialLine)
        # print("\n")

    # time.sleep(1)

    STLINK.write(b'p')
    # #Endlessly read serial port
    EndlesslyMonitorSerialPort(STLINK)

