import bk8500, time

###################################################################
#                               Init                              #
###################################################################
def Init(SerialObj, baudrate, parity, timeout):
    
    SerialObj.baudrate = baudrate
    SerialObj.parity = parity
    SerialObj.timeout = timeout
    SerialObj.open

###################################################################
#                          SetCurrent_A                           #
###################################################################
def SetCurrent_A(SerialObj, SerialAdd, Current_A):

    bk8500.set_remote(SerialObj, SerialAdd, True)
    bk8500.enable_input(SerialObj, SerialAdd, True)
    bk8500.set_current(SerialObj, SerialAdd, Current_A)
    time.sleep(0.2)

###################################################################
#                       SetSafetySettings                         #
###################################################################
def SetSafetySettings(Serial, Add, MaxCurr_A, MaxPower_W):

    #set remote
    bk8500.set_remote(Serial, Add, True)

    #Set absolute safety values
    bk8500.set_max_current(Serial, Add, MaxCurr_A)
    bk8500.set_max_power(Serial, Add, MaxPower_W)
    bk8500.set_mode(Serial, Add, "CC")