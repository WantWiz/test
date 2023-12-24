# bk8500.py, module version 1.0, downloaded from: www.TolisDIY.com

# This module is aimed at communicating with the BK Precision 8500 DC electronic load series
# module was tested on a BK Precision 8500 (120V/30A/300W) instrument

# 8500 series manual doesn't contain any remote command for V/I range control, nor for VOLTAGE ON/OFF SET parameters
# because of this, there are no functions in this module to control these parameters. Same is true for reading the Ah
# value from the battery test function which the manual doesn't include
# According to BK Precision support, there are no remote commands for these functions.
# There are some workaround for these issues though:
# For the range selection, use the Limits (current/voltage), when the limit is set to a value within the higher resolution
# range, the instrument will change to the lower range automatically, the function below will report the extra digit
# For the VOLTAGE ON/OFF set control, its possible to monitor the voltage and set input to on/off accordingly
# For the battery capacity, it possible to calculate the capacity by logging the current/power readings throughout the measurement

# instrument default address is '0', verify in instrument menu along with COM port settings in the instrument menu if needed



# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- #
#       List of function names for commands implemented in this module          #
# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- #

# Command group: py_function_name (byte/opcode), py_function_name (byte/opcode), ...

# Return data: get_response (0x12)

# Remote: set_remote (0x20)

# On/off: enable_input (0x21)

# Maximum parameter value: set_max_voltage (0x22), get_max_voltage (0x23), set_max_current (0x24),
# get_max_current (0x25), set_max_power (0x26), get_max_power (0x27)

# Operating mode: set_mode (0x28), get_mode (0x29)

# Mode parameters: set_current (0x2a), get_current (0x2b), set_voltage (0x2c), get_voltage (0x2d),
# set_power (0x2e), get_power (0x2f), set_resistance (0x30), get_resistance (0x31)

# Transient parameters: set_tran_CC_param (0x32), get_tran_CC_param (0x33), set_tran_CV_param (0x34),
# get_tran_CV_param (0x35), set_tran_CW_param (0x36), get_tran_CW_param (0x37), set_tran_CR_param (0x38),
# get_tran_CR_param (0x39)

# List operations: set_list_mode (0x3a), get_list_mode (0x3b), set_list_repeat (0x3c), get_list_repeat (0x3d),
# set_list_length (0x3e), get_list_length (0x3f), set_list_CC_param (0x40), get_list_CC_param (0x41),
# set_list_CV_param (0x42), get_list_CV_param (0x43), set_list_CW_param (0x44), get_list_CW_param (0x45),
# set_list_CR_param (0x46), get_list_CR_param (0x47),set_list_name (0x48), get_list_name (0x49),
# set_lists_partition (0x4a), get_lists_partition (0x4b), store_list_file (0x4c), recall_list_file (0x4d)

# Battery: set_battery_vmin (0x4e), get_battery_vmin (0x4f)

# Load on: set_load_timer_value (0x50), get_load_timer_value (0x51), set_load_timer_mode (0x52),
# get_load_timer_mode (0x53)

# Address: set_address (0x54)

# Local: set_local_control_bypass (0x55)

# Remote Sensing: set_remote_sense (0x56), get_remote_sense (0x57)

# Triggering: set_trig_source (0x58), get_trig_source (0x59), trig_instrument (0x5a)

# Store/recall: store_settings (0x5b), recall_setting (0x5c)

# Function: set_function (0x5d), get_function (0x5e)

# Read display values: get_instrument_readings (0x5f), get_instrument_state (0x5f)

# Product information: get_product_info (0x6a)


# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- #
#          constants and definitions needed through the module                  #
# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- #


empty_cmd = [0xaa]
empty_cmd.extend([0]*25)
empty_cmd_2 = [0] * 2
empty_cmd_4 = [0] * 4



# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- #
#       main functions to communicate with the BK-Precision 8500                #
# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- #


# get response from instrument and verify it is correct
# gets serial port object as arg
def get_response(ser):
    response = ser.read(26)
    if (len(response) != 26):           #check the received data has the full 26bytes
        print("No valid response received from instrument")
    else:                               #check the received data has proper checksum
        if (response[25] != sum(response[0:25]) % 256):
            print("Checksum error on received response")
        else:
            if (response[2] == 0x12):       #check the received data is the status of last command
                if (response[3] == 0x90):
                    print("Instrument responded with \"Checksum incorrect\"")
                elif (response[3] == 0xA0):
                    print("Instrument responded with \"Parameter incorrect\"")
                elif (response[3] == 0xB0):
                    print("Instrument responded with \"Unrecognized command\"")
                elif (response[3] == 0xC0):
                    print("Instrument responded with \"Invalid command\"")
                elif (response[3] == 0x80):
                    print("Instrument responded with \"Command was successful\"")
                else:       #this will be the case for every reading of status/value of the instrument
                    pass
            else:
                pass
    return response


# set instrument to remote(True)/local(False) control mode
# gets serial port object, instrument address, and True/False as args
def set_remote(ser,address,value):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x20
    if (value):
        cmd[3] = 0x01
    else:
        cmd[3] = 0x00
    print("Setting instrument to remote = " + str(bool(value)))
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# enable(True)/disable(False) input current on the load
# gets serial port object, instrument address, and True/False as args
def enable_input(ser,address,value):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x21
    if (value):
        cmd[3] = 0x01
    else:
        cmd[3] = 0x00
    print("Setting instrument input on = " + str(bool(value)))
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# set instrument max voltage
# gets serial port object, instrument address, and desired value as args
def set_max_voltage(ser,address,value):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x22
    cmd[3:7] = prep_cmd_volt_res_pow(value)
    print("Setting instrument max voltage = " + str(value) + "[V]")
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument max voltage
# gets serial port object, and instrument address as args
def get_max_voltage(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x23
    ser.write(modify_checksum(cmd))
    value = round(prep_response_volt_res_pow(get_response(ser)[3:7]),3)
    print("Instrument max voltage reported = " + str(value) + "[V]")
    return value


# set instrument max current
# gets serial port object, instrument address, and desired value as args
def set_max_current(ser,address,value):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x24
    cmd[3:7] = prep_cmd_cur(value)
    print("Setting instrument max current = " + str(value) + "[A]")
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument max current
# gets serial port object, and instrument address as args
def get_max_current(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x25
    ser.write(modify_checksum(cmd))
    value = round(prep_response_cur(get_response(ser)[3:7]),4)
    print("Instrument max current reported = " + str(value) + "[A]")
    return value


# set instrument max power
# gets serial port object, instrument address, and desired value as args
def set_max_power(ser,address,value):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x26
    cmd[3:7] = prep_cmd_volt_res_pow(value)
    print("Setting instrument max power = " + str(value) + "[W]")
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument max power
# gets serial port object, and instrument address as args
def get_max_power(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x27
    ser.write(modify_checksum(cmd))
    value = round(prep_response_volt_res_pow(get_response(ser)[3:7]),3)
    print("Instrument max power reported = " + str(value) + "[W]")
    return value


# set instrument mode (CC/CV/CW/CR)
# gets serial port object, instrument address, and desired mode as args
def set_mode(ser,address,mode):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x28
    if (mode == "CC"):
        cmd[3] = 0x00
    elif (mode == "CV"):
        cmd[3] = 0x01
    elif (mode == "CW"):
        cmd[3] = 0x02
    elif (mode == "CR"):
        cmd[3] = 0x03
    else:
        print("Invalid mode selected")
        return
    print("Setting instrument mode = " + mode)
    ser.write(modify_checksum(cmd))
    return get_response(ser)

# get instrument mode (CC/CV/CW/CR)
# gets serial port object, and instrument address as args
def get_mode(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x29
    ser.write(modify_checksum(cmd))
    mode = int(get_response(ser)[3])
    if (mode == 0):
        print("Instrument mode reported as \"CC\"")
        return "CC"
    elif (mode == 1):
        print("Instrument mode reported as \"CV\"")
        return "CV"
    elif (mode == 2):
        print("Instrument mode reported as \"CW\"")
        return "CW"
    elif (mode == 3):
        print("Instrument mode reported as \"CR\"")
        return "CR"
    else:
        print("Invalid mode reported by instrument")
        return "NA"


# set instrument CC current
# gets serial port object, instrument address, and desired value as args
def set_current(ser,address,value):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x2a
    cmd[3:7] = prep_cmd_cur(value)
    print("Setting instrument current = " + str(value) + "[A]")
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument CC current
# gets serial port object, and instrument address as args
def get_current(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x2b
    ser.write(modify_checksum(cmd))
    value = round(prep_response_cur(get_response(ser)[3:7]),4)
    print("Instrument current reported = " + str(value) + "[A]")
    return value


# set instrument CV voltage
# gets serial port object, instrument address, and desired value as args
def set_voltage(ser,address,value):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x2c
    cmd[3:7] = prep_cmd_volt_res_pow(value)
    print("Setting instrument voltage = " + str(value) + "[V]")
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument CV voltage
# gets serial port object, and instrument address as args
def get_voltage(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x2d
    ser.write(modify_checksum(cmd))
    value = round(prep_response_volt_res_pow(get_response(ser)[3:7]),3)
    print("Instrument voltage reported = " + str(value) + "[V]")
    return value


# set instrument CW power
# gets serial port object, instrument address, and desired value as args
def set_power(ser,address,value):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x2e
    cmd[3:7] = prep_cmd_volt_res_pow(value)
    print("Setting instrument power = " + str(value) + "[W]")
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument CW power
# gets serial port object, and instrument address as args
def get_power(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x2f
    ser.write(modify_checksum(cmd))
    value = round(prep_response_volt_res_pow(get_response(ser)[3:7]),3)
    print("Instrument power reported = " + str(value) + "[W]")
    return value


# set instrument CR resistance
# gets serial port object, instrument address, and desired value as args
def set_resistance(ser,address,value):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x30
    cmd[3:7] = prep_cmd_volt_res_pow(value)
    print("Setting instrument resistance = " + str(value) + "[Ohm]")
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument CR resistance
# gets serial port object, and instrument address as args
def get_resistance(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x31
    ser.write(modify_checksum(cmd))
    value = round(prep_response_volt_res_pow(get_response(ser)[3:7]),3)
    print("Instrument resistance reported = " + str(value) + "[Ohm]")
    return value


# set instrument CC transient mode setting
# gets serial port object, instrument address, and desired values as args
# values are: IA[A],TA[s],IB[A],TB[s], op(CONtinuous/PULse/TOGgled)
# op part in upper case must be included, rest is optional. case insensitive
def set_tran_CC_param(ser,address,IA,TA,IB,TB,op):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x32
    cmd[3:7] = prep_cmd_cur(IA)
    cmd[7:9] = prep_cmd_cur(TA)[:2]        #use of prep_cmd_cur as it has same unit (0.1m) as current, only use allowed digits
    cmd[9:13] = prep_cmd_cur(IB)
    cmd[13:15] = prep_cmd_cur(TB)[:2]      #use of prep_cmd_cur as it has same unit (0.1m) as current, only use allowed digits
    if ("CON" == op[0:3].upper()):
        cmd[15] = 0x00
        op = "CONTINUOUS"
    elif ("PUL" == op[0:3].upper()):
        cmd[15] = 0x01
        op = "PULSE"
    elif ("TOG" == op[0:3].upper()):
        cmd[15] = 0x02
        op = "TOGGLED"
    else:
        print("Invalid mode selected")
        return
    print("Setting instrument CC transient params = " + str(IA) + "[A], " + str(TA) + "[s], " + str(IB) + "[A], " + str(TB) + "[s], " + op)
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument CC transient mode setting
# gets serial port object, and instrument address as args
# values are: IA[A],TA[s],IB[A],TB[s],op
def get_tran_CC_param(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x33
    values = [0] * 5
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    values[0] = round(prep_response_cur(response[3:7]),4)
    values[1] = round(prep_response_cur(response[7:9]),4)        #use of prep_cmd_cur as it has same unit (0.1m) as current, only use last 4 digits
    values[2] = round(prep_response_cur(response[9:13]),4)
    values[3] = round(prep_response_cur(response[13:15]),4)      #use of prep_cmd_cur as it has same unit (0.1m) as current, only use last 4 digits
    values[4] = cmd[15]
    if (values[4] == 0):
        op = "CONTINUOUS"
    elif (values[4] == 1):
        op = "PULSE"
    elif (values[4] == 2):
        op = "TOGGLED"
    else:
        op = "ERROR"
    print("Instrument CC transient params reported = " + str(values[0]) + "[A], " + str(values[1]) + "[s], " + str(values[2]) + "[A], " + str(values[3]) + "[s], " + op)
    return values


# set instrument CV transient mode setting
# gets serial port object, instrument address, and desired values as args
# values are: VA[V],TA[s],VB[V],TB[s], op(CONtinuous/PULse/TOGgled)
# op part in upper case must be included, rest is optional. case insensitive
def set_tran_CV_param(ser,address,VA,TA,VB,TB,op):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x34
    cmd[3:7] = prep_cmd_volt_res_pow(VA)
    cmd[7:9] = prep_cmd_cur(TA)[:2]        #use of prep_cmd_cur as it has same unit (0.1m) as current, only use allowed digits
    cmd[9:13] = prep_cmd_volt_res_pow(VB)
    cmd[13:15] = prep_cmd_cur(TB)[:2]      #use of prep_cmd_cur as it has same unit (0.1m) as current, only use allowed digits
    if ("CON" == op[0:3].upper()):
        cmd[15] = 0x00
        op = "CONTINUOUS"
    elif ("PUL" == op[0:3].upper()):
        cmd[15] = 0x01
        op = "PULSE"
    elif ("TOG" == op[0:3].upper()):
        cmd[15] = 0x02
        op = "TOGGLED"
    else:
        print("Invalid mode selected")
        return
    print("Setting instrument CV transient params = " + str(VA) + "[V], " + str(TA) + "[s], " + str(VB) + "[V], " + str(TB) + "[s], " + op)
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument CV transient mode setting
# gets serial port object, and instrument address as args
# values are: VA[V],TA[s],VB[V],TB[s],op
def get_tran_CV_param(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x35
    values = [0] * 5
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    values[0] = round(prep_response_volt_res_pow(response[3:7]),3)
    values[1] = round(prep_response_cur(response[7:9]),4)        #use of prep_cmd_cur as it has same unit (0.1m) as current, only use last 4 digits
    values[2] = round(prep_response_volt_res_pow(response[9:13]),3)
    values[3] = round(prep_response_cur(response[13:15]),4)      #use of prep_cmd_cur as it has same unit (0.1m) as current, only use last 4 digits
    values[4] = cmd[15]
    if (values[4] == 0):
        op = "CONTINUOUS"
    elif (values[4] == 1):
        op = "PULSE"
    elif (values[4] == 2):
        op = "TOGGLED"
    else:
        op = "ERROR"
    print("Instrument CV transient params reported = " + str(values[0]) + "[V], " + str(values[1]) + "[s], " + str(values[2]) + "[V], " + str(values[3]) + "[s], " + op)
    return values


# set instrument CW transient mode setting
# gets serial port object, instrument address, and desired values as args
# values are: WA[V],TA[s],WB[V],TB[s], op(CONtinuous/PULse/TOGgled)
# op part in upper case must be included, rest is optional. case insensitive
def set_tran_CW_param(ser,address,WA,TA,WB,TB,op):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x36
    cmd[3:7] = prep_cmd_volt_res_pow(WA)
    cmd[7:9] = prep_cmd_cur(TA)[:2]        #use of prep_cmd_cur as it has same unit (0.1m) as current, only use allowed digits
    cmd[9:13] = prep_cmd_volt_res_pow(WB)
    cmd[13:15] = prep_cmd_cur(TB)[:2]      #use of prep_cmd_cur as it has same unit (0.1m) as current, only use allowed digits
    if ("CON" == op[0:3].upper()):
        cmd[15] = 0x00
        op = "CONTINUOUS"
    elif ("PUL" == op[0:3].upper()):
        cmd[15] = 0x01
        op = "PULSE"
    elif ("TOG" == op[0:3].upper()):
        cmd[15] = 0x02
        op = "TOGGLED"
    else:
        print("Invalid mode selected")
        return
    print("Setting instrument CW transient params = " + str(WA) + "[W], " + str(TA) + "[s], " + str(WB) + "[W], " + str(TB) + "[s], " + op)
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument CW transient mode setting
# gets serial port object, and instrument address as args
# values are: WA[V],TA[s],WB[V],TB[s],op
def get_tran_CW_param(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x37
    values = [0] * 5
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    values[0] = round(prep_response_volt_res_pow(response[3:7]),3)
    values[1] = round(prep_response_cur(response[7:9]),4)        #use of prep_cmd_cur as it has same unit (0.1m) as current, only use last 4 digits
    values[2] = round(prep_response_volt_res_pow(response[9:13]),3)
    values[3] = round(prep_response_cur(response[13:15]),4)      #use of prep_cmd_cur as it has same unit (0.1m) as current, only use last 4 digits
    values[4] = cmd[15]
    if (values[4] == 0):
        op = "CONTINUOUS"
    elif (values[4] == 1):
        op = "PULSE"
    elif (values[4] == 2):
        op = "TOGGLED"
    else:
        op = "ERROR"
    print("Instrument CW transient params reported = " + str(values[0]) + "[W], " + str(values[1]) + "[s], " + str(values[2]) + "[W], " + str(values[3]) + "[s], " + op)
    return values


# set instrument CR transient mode setting
# gets serial port object, instrument address, and desired values as args
# values are: RA[V],TA[s],RB[V],TB[s], op(CONtinuous/PULse/TOGgled)
# op part in upper case must be included, rest is optional. case insensitive
def set_tran_CR_param(ser,address,RA,TA,RB,TB,op):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x38
    cmd[3:7] = prep_cmd_volt_res_pow(RA)
    cmd[7:9] = prep_cmd_cur(TA)[:2]        #use of prep_cmd_cur as it has same unit (0.1m) as current, only use allowed digits
    cmd[9:13] = prep_cmd_volt_res_pow(RB)
    cmd[13:15] = prep_cmd_cur(TB)[:2]      #use of prep_cmd_cur as it has same unit (0.1m) as current, only use allowed digits
    if ("CON" == op[0:3].upper()):
        cmd[15] = 0x00
        op = "CONTINUOUS"
    elif ("PUL" == op[0:3].upper()):
        cmd[15] = 0x01
        op = "PULSE"
    elif ("TOG" == op[0:3].upper()):
        cmd[15] = 0x02
        op = "TOGGLED"
    else:
        print("Invalid mode selected")
        return
    print("Setting instrument CR transient params = " + str(RA) + "[Ohm], " + str(TA) + "[s], " + str(RB) + "[Ohm], " + str(TB) + "[s], " + op)
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument CR transient mode setting
# gets serial port object, and instrument address as args
# values are: VA[V],TA[s],VB[V],TB[s],op
def get_tran_CR_param(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x39
    values = [0] * 5
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    values[0] = round(prep_response_volt_res_pow(response[3:7]),3)
    values[1] = round(prep_response_cur(response[7:9]),4)        #use of prep_cmd_cur as it has same unit (0.1m) as current, only use last 4 digits
    values[2] = round(prep_response_volt_res_pow(response[9:13]),3)
    values[3] = round(prep_response_cur(response[13:15]),4)      #use of prep_cmd_cur as it has same unit (0.1m) as current, only use last 4 digits
    values[4] = cmd[15]
    if (values[4] == 0):
        op = "CONTINUOUS"
    elif (values[4] == 1):
        op = "PULSE"
    elif (values[4] == 2):
        op = "TOGGLED"
    else:
        op = "ERROR"
    print("Instrument CR transient params reported = " + str(values[0]) + "[Ohm], " + str(values[1]) + "[s], " + str(values[2]) + "[Ohm], " + str(values[3]) + "[s], " + op)
    return values


# set instrument mode (CC/CV/CW/CR) for the list
# gets serial port object, instrument address, and desired mode as args
def set_list_mode(ser,address,mode):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x3a
    if (mode == "CC"):
        cmd[3] = 0x00
    elif (mode == "CV"):
        cmd[3] = 0x01
    elif (mode == "CW"):
        cmd[3] = 0x02
    elif (mode == "CR"):
        cmd[3] = 0x03
    else:
        print("Invalid list mode selected")
        return
    print("Setting list mode = " + mode)
    ser.write(modify_checksum(cmd))
    return get_response(ser)

# get instrument mode (CC/CV/CW/CR) for the list
# gets serial port object, and instrument address as args
def get_list_mode(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x3b
    ser.write(modify_checksum(cmd))
    mode = int(get_response(ser)[3])
    if (mode == 0):
        print("Instrument list mode reported as \"CC\"")
        return "CC"
    elif (mode == 1):
        print("Instrument list mode reported as \"CV\"")
        return "CV"
    elif (mode == 2):
        print("Instrument list mode reported as \"CW\"")
        return "CW"
    elif (mode == 3):
        print("Instrument list mode reported as \"CR\"")
        return "CR"
    else:
        print("Invalid list mode reported by instrument")
        return "NA"


# set list repeat mode to repeat/single (Enabled/Disabled)
# gets serial port object, instrument address, and True/False as args
def set_list_repeat(ser,address,value):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x3c
    if (value):
        cmd[3] = 0x01
    else:
        cmd[3] = 0x00
    print("Setting list repeat = " + str(bool(value)))
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get list repeat mode repeat/single (Enabled/Disabled)
# gets serial port object, and instrument address as args
def get_list_repeat(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x3d
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    if response[3]:
        value = True
    else:
        value = False
    print("Instrument reported list repeat = " + str(value))
    return value


# set list length (number of steps)
# gets serial port object, instrument address, and desired value as args
def set_list_length(ser,address,value):
    if (value < 1 or value > 1000):
        print("Invalid list length, valid range is 1 to 1000")
        return
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x3e
    cmd[3] = value % 256
    cmd[4] = int(value / 256)
    print("Setting list length to " + str(value) + " steps")
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get list length (number of steps)
# gets serial port object, and instrument address as args
def get_list_length(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x3f
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    value = response[4] * 256 + response[3]
    print("Instrument reported list length as " + str(value) + " steps")
    return value


# set instrument CC transient mode setting
# gets serial port object, instrument address, and desired values as args
# values are: step[#], Istep[A], Tstep[s]
def set_list_CC_param(ser,address,step_num,Istep,Tstep):
    if (step_num < 1 or step_num > 1000):
        print("Invalid step number, valid range is 1 to 1000")
        return
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x40
    cmd[3] = step_num % 256
    cmd[4] = int(step_num / 256)
    cmd[5:9] = prep_cmd_cur(Istep)
    cmd[9:11] = prep_cmd_cur(Tstep)[:2]      #use of prep_cmd_cur as it has same unit (0.1m) as current, only use allowed digits
    print("Setting instrument CC list params, step " + str(step_num) + ": Current = " + str(Istep) + "[A], Duration = " + str(Tstep) + "[s]")
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument CC transient mode setting
# gets serial port object, and instrument address as args
# values are: step[#], Istep[A], Tstep[s]
def get_list_CC_param(ser,address,step_num):
    if (step_num < 1 or step_num > 1000):
        print("Invalid step number, valid range is 1 to 1000")
        return
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x41
    cmd[3] = step_num % 256
    cmd[4] = int(step_num / 256)
    values = [0] * 3
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    values[0] = step_num
    values[1] = round(prep_response_cur(response[5:9]),4)
    values[2] = round(prep_response_cur(response[9:11]),2)      #use of prep_cmd_cur as it has same unit (0.1m) as current, only use last 4 digits
    print("Instrument reported CC list params, step " + str(values[0]) + ": Current = " + str(values[1]) + "[A], Duration = " + str(values[2]) + "[s]")
    return values


# set instrument CV transient mode setting
# gets serial port object, instrument address, and desired values as args
# values are: step[#], Vstep[V], Tstep[s]
def set_list_CV_param(ser,address,step_num,Vstep,Tstep):
    if (step_num < 1 or step_num > 1000):
        print("Invalid step number, valid range is 1 to 1000")
        return
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x42
    cmd[3] = step_num % 256
    cmd[4] = int(step_num / 256)
    cmd[5:9] = prep_cmd_volt_res_pow(Vstep)
    cmd[9:11] = prep_cmd_cur(Tstep)[:2]      #use of prep_cmd_cur as it has same unit (0.1m) as current, only use allowed digits
    print("Setting instrument CV list params, step " + str(step_num) + ": Voltage = " + str(Vstep) + "[V], Duration = " + str(Tstep) + "[s]")
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument CV transient mode setting
# gets serial port object, and instrument address as args
# values are: step[#], Vstep[V], Tstep[s]
def get_list_CV_param(ser,address,step_num):
    if (step_num < 1 or step_num > 1000):
        print("Invalid step number, valid range is 1 to 1000")
        return
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x43
    cmd[3] = step_num % 256
    cmd[4] = int(step_num / 256)
    values = [0] * 3
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    values[0] = step_num
    values[1] = round(prep_response_volt_res_pow(response[5:9]),4)
    values[2] = round(prep_response_cur(response[9:11]),2)      #use of prep_cmd_cur as it has same unit (0.1m) as current, only use last 4 digits
    print("Instrument reported CV list params, step " + str(values[0]) + ": Voltage = " + str(values[1]) + "[V], Duration = " + str(values[2]) + "[s]")
    return values


# set instrument CW transient mode setting
# gets serial port object, instrument address, and desired values as args
# values are: step[#], Wstep[W], Tstep[s]
def set_list_CW_param(ser,address,step_num,Wstep,Tstep):
    if (step_num < 1 or step_num > 1000):
        print("Invalid step number, valid range is 1 to 1000")
        return
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x44
    cmd[3] = step_num % 256
    cmd[4] = int(step_num / 256)
    cmd[5:9] = prep_cmd_volt_res_pow(Wstep)
    cmd[9:11] = prep_cmd_cur(Tstep)[:2]      #use of prep_cmd_cur as it has same unit (0.1m) as current, only use allowed digits
    print("Setting instrument CW list params, step " + str(step_num) + ": Power = " + str(Wstep) + "[W], Duration = " + str(Tstep) + "[s]")
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument CW transient mode setting
# gets serial port object, and instrument address as args
# values are: step[#], Wstep[W], Tstep[s]
def get_list_CW_param(ser,address,step_num):
    if (step_num < 1 or step_num > 1000):
        print("Invalid step number, valid range is 1 to 1000")
        return
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x45
    cmd[3] = step_num % 256
    cmd[4] = int(step_num / 256)
    values = [0] * 3
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    values[0] = step_num
    values[1] = round(prep_response_volt_res_pow(response[5:9]),4)
    values[2] = round(prep_response_cur(response[9:11]),2)      #use of prep_cmd_cur as it has same unit (0.1m) as current, only use last 4 digits
    print("Instrument reported CW list params, step " + str(values[0]) + ": Power = " + str(values[1]) + "[W], Duration = " + str(values[2]) + "[s]")
    return values


# set instrument CR transient mode setting
# gets serial port object, instrument address, and desired values as args
# values are: step[#], Rstep[Ohm],Tstep[s]
def set_list_CR_param(ser,address,step_num,Rstep,Tstep):
    if (step_num < 1 or step_num > 1000):
        print("Invalid step number, valid range is 1 to 1000")
        return
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x46
    cmd[3] = step_num % 256
    cmd[4] = int(step_num / 256)
    cmd[5:9] = prep_cmd_volt_res_pow(Rstep)
    cmd[9:11] = prep_cmd_cur(Tstep)[:2]      #use of prep_cmd_cur as it has same unit (0.1m) as current, only use allowed digits
    print("Setting instrument CR list params, step " + str(step_num) + ": Resistance = " + str(Rstep) + "[Ohm], Duration = " + str(Tstep) + "[s]")
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument CR transient mode setting
# gets serial port object, and instrument address as args
# values are: step[#], Rstep[A], Tstep[s]
def get_list_CR_param(ser,address,step_num):
    if (step_num < 1 or step_num > 1000):
        print("Invalid step number, valid range is 1 to 1000")
        return
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x47
    cmd[3] = step_num % 256
    cmd[4] = int(step_num / 256)
    values = [0] * 3
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    values[0] = step_num
    values[1] = round(prep_response_volt_res_pow(response[5:9]),4)
    values[2] = round(prep_response_cur(response[9:11]),2)      #use of prep_cmd_cur as it has same unit (0.1m) as current, only use last 4 digits
    print("Instrument reported CR list params, step " + str(values[0]) + ": Resistance = " + str(values[1]) + "[Ohm], Duration = " + str(values[2]) + "[s]")
    return values


# set list filename
# gets serial port object, instrument address, and desired name as args
def set_list_name(ser,address,name):
    if (len(name) < 1 or len(name) > 10):
        print("Invalid name length, valid length is 1 to 10 characters")
        return
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x48
    for i in range(len(name)):
        cmd[3+i] = ord(name[i])
    print("Setting list name to \"" + name + "\"")
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get list filename
# gets serial port object, and instrument address as args
def get_list_name(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x49
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    name = ""
    i = 3
    while (response[i] != 0 and i < 13):
        name = name + chr(response[i])
        i += 1
    print("Instrument reported list name as \"" + name + "\"")
    return name


# set memory partitioning number of list (1/2/4/8) with a length of (1000/500/250/120) steps each
# gets serial port object, instrument address, and number of slots as args
def set_lists_partition(ser,address,value):
    if (value != 1 and value != 2 and value != 4 and value != 8):
        print("Invalid value selected, lists memory partition scheme allowed is 1/2/4/8")
        return
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x4a
    cmd[3] = value
    list_length = int(1000 / value)
    if (value == 8):
        list_length = 120
    print("Setting memory partitioning to support " + str(value) + " lists, each " + str(list_length) + " steps long")
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get memory partitioning number of list (1/2/4/8) with a length of (1000/500/250/120) steps each
# gets serial port object, and instrument address as args
def get_lists_partition(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x4b
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    value = response[3]
    list_length = int(1000 / value)
    if (value == 8):
        list_length = 120
    print("Instrument reported memory partitioning to set to " + str(value) + " lists, each " + str(list_length) + " steps long")
    return value


# store the list file into memory at the selected slot
# gets serial port object, instrument address, and slot number of slots as args
def store_list_file(ser,address,value):
    if (value < 1 or value > 8):
        print("Invalid memory slot selected, value range is 1 to 8")
        return
    available_slots = get_lists_partition(ser,address)
    if (value > available_slots):
        print("Memory partitioning is current set to " + str(available_slots) + " lists, choose a memory slot in this range")
        return
    max_length = int(1000 / available_slots)
    if (available_slots == 8):
        max_length = 120
    list_length = get_list_length(ser,address)
    if (list_length > max_length):
        print("List is " + str(list_length) + " step long, current partitioning allows up to " + str(max_length) + "steps")
        return
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x4c
    cmd[3] = value
    print("Storing current list to slot " + str(value))
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# recall the list file into memory at the selected slot
# gets serial port object, instrument address, and slot number of slots as args
def recall_list_file(ser,address,value):
    if (value < 1 or value > 8):
        print("Invalid memory slot selected, value range is 1 to 8")
        return
    available_slots = get_lists_partition(ser,address)
    if (value > available_slots):
        print("Memory partitioning is current set to " + str(available_slots) + " lists, choose a memory slot in this range")
        return
    max_length = int(1000 / available_slots)
    if (available_slots == 8):
        max_length = 120
    list_length = get_list_length(ser, address)
    if (list_length > max_length):
        print("List is " + str(list_length) + " step long, current partitioning allows up to " + str(
            max_length) + "steps")
        return
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x4d
    cmd[3] = value
    print("Recalling current list from slot " + str(value))
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# set instrument Battery testing function minimum voltage
# gets serial port object, instrument address, and desired value as args
def set_battery_vmin(ser,address,value):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x4e
    cmd[3:7] = prep_cmd_volt_res_pow(value)
    print("Setting instrument battery testing minimum voltage = " + str(value) + "[V]")
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument Battery testing function minimum voltage
# gets serial port object, and instrument address as args
def get_battery_vmin(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x4f
    ser.write(modify_checksum(cmd))
    value = round(prep_response_volt_res_pow(get_response(ser)[3:7]),3)
    print("Instrument battery testing minimum voltage reported = " + str(value) + "[V]")
    return value


# set LOAD ON timer value
# gets serial port object, instrument address, and desired value in seconds as args
def set_load_timer_value(ser,address,value):
    if (value < 1 or value > 60000):
        print("Invalid timer value, valid range is 1[s] to 60,000[s]")
        return
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x50
    cmd[3] = value % 256
    cmd[4] = int(value / 256)
    print("Setting instrument LOAD ON timer value to " + str(value) + "[s]")
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get LOAD ON timer value
# gets serial port object, and instrument address as args
def get_load_timer_value(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x51
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    value = response[4] * 256 + response[3]
    print("Instrument LOAD ON timer value reported as " + str(value) + "[s]")
    return value


# set LOAD ON timer mode (Enabled/Disabled)
# gets serial port object, instrument address, and True/False as args
def set_load_timer_mode(ser,address,value):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x52
    if (value):
        cmd[3] = 0x01
    else:
        cmd[3] = 0x00
    print("Setting instrument LOAD ON timer Enable = " + str(bool(value)))
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get LOAD ON timer mode (Enabled/Disabled)
# gets serial port object, and instrument address as args
def get_load_timer_mode(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x53
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    if response[3]:
        value = True
    else:
        value = False
    print("Instrument reported LOAD ON timer Enable = " + str(value))
    return value


# set instrument address
# gets serial port object, instrument address, and desired address as args
def set_address(ser,address,value):
    if (value < 0 or value > 254):
        print("Invalid desired address value, valid range is 0 to 254")
        return
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x54
    cmd[3] = value
    print("Setting instrument address to " + str(value))
    print("NOTE: starting from next command, the instruments new address will be " + str(value))
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# set instrument front panel over-ride via "local" button to active(True)/inactive(False)
# gets serial port object, instrument address, and True/False as args
def set_local_control_bypass(ser,address,value):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x55
    if (value):
        cmd[3] = 0x01
    else:
        cmd[3] = 0x00
    print("Setting instrument front panel control bypass allowed = " + str(bool(value)))
    ser.write(modify_checksum(cmd))
    return get_response(ser)

# set instrument remote-sense active(True)/inactive(False)
# gets serial port object, instrument address, and True/False as args
def set_remote_sense(ser,address,value):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x56
    if (value):
        cmd[3] = 0x01
    else:
        cmd[3] = 0x00
    print("Setting instrument remote sense = " + str(bool(value)))
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument max voltage
# gets serial port object, and instrument address as args
def get_remote_sense(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x57
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    if response[3]:
        value = True
    else:
        value = False
    print("Instrument remote sense reported = " + str(value))
    return value


# set instrument trigger source (IMMediate/EXTernal/BUS)
# gets serial port object, instrument address, and desired mode as args
def set_trig_source(ser,address,mode):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x58
    if ("IMM" == mode[0:3].upper()):
        cmd[3] = 0x00
        mode = "IMMediate"
    elif ("EXT" == mode[0:3].upper()):
        cmd[3] = 0x01
        mode = "EXTernal"
    elif ("BUS" == mode[0:3].upper()):
        cmd[3] = 0x02
        mode = "BUS"
    else:
        print("Invalid trigger source selected")
        return
    print("Setting instrument trigger source = " + mode)
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument trigger source
# gets serial port object, and instrument address as args
def get_trig_source(ser, address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x59
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    value = response[3]
    if (value == 0):
        mode = "IMMediate"
    elif (value == 1):
        mode = "EXTERNAL"
    elif (value == 2):
        mode = "BUS"
    else:
        mode = "ERROR"
    print("Instrument trigger source reported = " + mode)
    return value


# trigger the instrument (BUS trigger command)
# gets serial port object, and instrument address as args
def trig_instrument(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x5a
    print("Sending trigger to instrument")
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# store instrument setting into slot number 1-25
# gets serial port object, instrument address, and slot number as args
def store_settings(ser,address,slot):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x5b
    if (slot > 0 and slot < 26):
        cmd[3] = slot
    else:
        print("Invalid slot selected, valid range is 1 to 25")
        return
    print("Storing instrument setting to slot #" + str(slot))
    ser.write(modify_checksum(cmd))
    return get_response(ser)

# recall instrument setting from slot number 1-25
# gets serial port object, instrument address, and slot number as args
def recall_settings(ser,address,slot):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x5c
    if (slot > 0 and slot < 26):
        cmd[3] = slot
    else:
        print("Invalid slot selected, valid range is 1 to 25")
        return
    print("Recalling instrument setting from slot #" + str(slot))
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# set instrument function (FIXed/SHOrt/TRAnsient/LISt/BATtery)
# gets serial port object, instrument address, and desired mode as args
def set_function(ser,address,mode):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x5d
    if ("FIX" == mode[0:3].upper()):
        cmd[3] = 0x00
        mode = "FIXED"
    elif ("SHO" == mode[0:3].upper()):
        cmd[3] = 0x01
        mode = "SHORT"
    elif ("TRA" == mode[0:3].upper()):
        cmd[3] = 0x02
        mode = "TRANSIENT"
    elif ("LIS" == mode[0:3].upper()):
        cmd[3] = 0x03
        mode = "LIST"
    elif ("BAT" == mode[0:3].upper()):
        cmd[3] = 0x04
        mode = "BATTERY"
    else:
        print("Invalid function selected")
        return
    print("Setting instrument function = " + mode)
    ser.write(modify_checksum(cmd))
    return get_response(ser)


# get instrument function
# gets serial port object, and instrument address as args
def get_function(ser, address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x5e
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    value = response[3]
    if (value == 0):
        mode = "FIXED"
    elif (value == 1):
        mode = "SHORT"
    elif (value == 2):
        mode = "TRANSIENT"
    elif (value == 3):
        mode = "LIST"
    elif (value == 4):
        mode = "BATTERY"
    else:
        mode = "ERROR"
    print("Instrument function reported = " + mode)
    return value


# get input voltage, current,and  power
# gets serial port object, and instrument address as args
def get_instrument_readings(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x5f
    values = [0] * 3
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    values[0] = round(prep_response_volt_res_pow(response[3:7]), 3)
    values[1] = round(prep_response_cur(response[7:11]), 4)
    values[2] = round(prep_response_volt_res_pow(response[11:15]), 3)
    print("Instrument reported VIN=" + str(values[0]) + "[V], Current=" + str(values[1]) + "[A], Power=" + str(values[2]) + "[W]")
    return values


# get input voltage, current, power, and relative state
# gets serial port object, and instrument address as args
# similar to get_instrument_readings, but also uses 'Operation-state' and 'Demand-state' part of response
def get_instrument_state(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x5f
    values = [0] * 20
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    values[0] = round(prep_response_volt_res_pow(response[3:7]),3)
    values[1] = round(prep_response_cur(response[7:11]),4)
    values[2] = round(prep_response_volt_res_pow(response[11:15]),3)
    temp = response[15]
    for i in range(7):
        values[i+3] = temp % 2
        temp = int(temp / 2)
    temp = response[16]
    for i in range(8):
        values[i+10] = temp % 2
        temp = int(temp / 2)
    temp = response[17]
    for i in range(2):
        values[i+18] = temp % 2
        temp = int(temp / 2)
    print("Instrument reported VIN=" + str(values[0]) + "[V], Current=" + str(values[1]) + "[A], Power=" + str(values[2]) + "[W]")
    print("Instrument Operation-state register content:")
    print("0: Calculate the new demarcation coefficient = " + str(bool(values[3])))
    print("1: Waiting for a trigger signal = " + str(bool(values[4])))
    print("2: Remote control state = " + str(bool(values[5])))
    print("3: Output (enabled) state = " + str(bool(values[6])))
    print("4: Local key (enable bypass) state = " + str(bool(values[7])))
    print("5: Remote sensing mode = " + str(bool(values[8])))
    print("6: LOAD ON timer is enabled = " + str(bool(values[9])))
    print("Instrument Demand-state register content:")
    print("0: Reverse voltage at instrument's terminals = " + str(bool(values[10])))
    print("1: Over voltage = " + str(bool(values[11])))
    print("2: Over current = " + str(bool(values[12])))
    print("3: Over power = " + str(bool(values[13])))
    print("4: Over temperature = " + str(bool(values[14])))
    print("5: Not connected remote terminal = " + str(bool(values[15])))
    print("6: Constant current (reached set value) = " + str(bool(values[16])))
    print("7: Constant voltage (reached set value) = " + str(bool(values[17])))
    print("8: Constant power (reached set value) = " + str(bool(values[18])))
    print("9: Constant resistance (reached set value) = " + str(bool(values[19])))
    return values


# get instrument information including model, version, and serial number
# gets serial port object, and instrument address as args
def get_product_info(ser,address):
    cmd = empty_cmd
    cmd[1] = address
    cmd[2] = 0x6a
    info = ["NA"] * 3
    print("Asking instrument for product information")
    ser.write(modify_checksum(cmd))
    response = get_response(ser)
    info[0] = response[3:8].decode('utf-8')[0:4]
    info[1] = str(hex(response[9]).lstrip("0x")) + "." + str(hex(response[8]).lstrip("0x"))
    info[2] = response[10:20].decode('utf-8')
    print("Instrument reported model:" + info[0] + ", version:" + info[1] + ", serial number:" + info[2])
    return info




# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- #
#               support functions  called from within the module                #
# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- #

# modify last byte of data with correct checksum
# gets desired command line to be sent as arg
def modify_checksum(cmd):
    if (len(cmd) == 26):
        cmd[25] = sum(cmd[0:25]) % 256
    else:
        print("Command isn't right length!")
    return cmd


# return command portion with 4 bytes of the value, unit in 1(volt/ohm/watt), for current scale from 0.1!
# gets value as arg
def prep_cmd_volt_res_pow(value):
    value = value * 1000
    value = hex(int(value))[2:]
    value = value.zfill(8)[-8:]     #fill to 8 digits, limit to 8 digits
    cmd_4 = empty_cmd_4
    cmd_4[0] = int(value[6:8], 16)
    cmd_4[1] = int(value[4:6], 16)
    cmd_4[2] = int(value[2:4], 16)
    cmd_4[3] = int(value[0:2], 16)
    return cmd_4


# addon to previous function (prep_cmd_volt_res_pow) for currents
# gets value as arg
def prep_cmd_cur(value):
    cmd_4 = prep_cmd_volt_res_pow(value*10)
    return cmd_4


# translate incoming response into value contained, unit in 1(volt/ohm/watt), for current scale from 0.1!
# gets response as arg
def prep_response_volt_res_pow(response):
    value = 0
    for i in range(len(response)):
        value = value * 256 + response[len(response) -1 - i]
    return value/1000


# addon to previous function (prep_response_volt_res_pow) for currents
# gets response as arg
def prep_response_cur(response):
    return prep_response_volt_res_pow(response)/10
