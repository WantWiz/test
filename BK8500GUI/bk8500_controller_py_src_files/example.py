import bk8500
import serial


address = 0
ser = serial.Serial()
ser.baudrate = 9600
ser.port = 'COM9'
ser.parity = 'N'
ser.timeout = 2
print(ser)
ser.open()
print(ser.is_open)

#set remote
bk8500.set_remote(ser,address,True)

#enable input
bk8500.enable_input(ser,address,True)

#set max voltage
bk8500.set_max_voltage(ser,address,120)

#get max voltage
bk8500.get_max_voltage(ser,address)
#set current
bk8500.set_current(ser,address,3.2)

#get current
bk8500.get_current(ser,address)

#set power
bk8500.set_power(ser,address,115)

#get power
bk8500.get_power(ser,address)

#set transient CV params
bk8500.set_tran_CC_param(ser,address,1,2,3,4,"con")

#get transient CV params
bk8500.get_tran_CC_param(ser,address)

#set resistance
bk8500.set_resistance(ser,address,470)

#get resistance
bk8500.get_resistance(ser,address)

#disable input
bk8500.enable_input(ser,address,False)

#get product info
bk8500.get_product_info(ser,address)

#get input V/I/W readings
bk8500.get_instrument_readings(ser,address)

#get instrument readings + status registers
bk8500.get_instrument_state(ser,address)

#turn off remote sense
bk8500.set_remote_sense(ser,address,False)

#check if remote state is active
bk8500.get_remote_sense(ser,address)

#disable front panel "local" key bypass
bk8500.set_local_control_bypass(ser,address,False)

#set instrument trigger to BUS (remote control)
bk8500.set_trig_source(ser,address,"BUS")

#check trigger source
bk8500.get_trig_source(ser,address)

#send trigger over BUS
bk8500.trig_instrument(ser,address)

#store instrument settings to slot 25
bk8500.store_settings(ser,address,25)

#load instrument settings from slot 25
bk8500.recall_settings(ser,address,25)

#set and check the function of the instrument
bk8500.set_function(ser,address,"FIX")
bk8500.get_function(ser,address)
bk8500.set_function(ser,address,"SHORt")
bk8500.get_function(ser,address)
bk8500.set_function(ser,address,"transie")
bk8500.get_function(ser,address)
bk8500.set_function(ser,address,"list")
bk8500.get_function(ser,address)
bk8500.set_function(ser,address,"batt")
bk8500.get_function(ser,address)

#set and check vmin for battery function
bk8500.set_battery_vmin(ser,address,0.99)
bk8500.get_battery_vmin(ser,address)

#modify the timer value and on/off state
bk8500.set_load_timer_value(ser,address,60000)
bk8500.get_load_timer_value(ser,address)
bk8500.set_load_timer_mode(ser,address,True)
bk8500.get_load_timer_mode(ser,address)
bk8500.set_load_timer_mode(ser,address,False)
bk8500.get_load_timer_mode(ser,address)

#modify instrument address
new_address = 33
bk8500.set_address(ser,address,new_address)
address = new_address
#modify back to default address
new_address = 0
bk8500.set_address(ser,address,new_address)
address = new_address

#set list function selected mode and read it back
bk8500.set_list_mode(ser,address,"CW")
bk8500.get_list_mode(ser,address)
bk8500.set_list_mode(ser,address,"CV")
bk8500.get_list_mode(ser,address)
bk8500.set_list_mode(ser,address,"CR")
bk8500.get_list_mode(ser,address)
bk8500.set_list_mode(ser,address,"CC")
bk8500.get_list_mode(ser,address)

#set and check the length of current list
bk8500.set_list_length(ser,address,5)
bk8500.get_list_length(ser,address)

#set list to repeat
bk8500.set_list_repeat(ser,address,True)
bk8500.get_list_repeat(ser,address)
#set list to single shot
bk8500.set_list_repeat(ser,address,False)
bk8500.get_list_repeat(ser,address)

#set and check the values (current and time) of item 333 in the CC list
bk8500.set_list_CC_param(ser,address,333,5,3)
bk8500.get_list_CC_param(ser,address,333)
#same for item 3 in the CC list
bk8500.set_list_CC_param(ser,address,3,4.4,5.5)
bk8500.get_list_CC_param(ser,address,3)
#same for item 3 in the CV list
bk8500.set_list_CV_param(ser,address,3,4.4,5.5)
bk8500.get_list_CV_param(ser,address,3)
#same for item 3 in the CW list
bk8500.set_list_CW_param(ser,address,3,4.4,5.5)
bk8500.get_list_CW_param(ser,address,3)
#same for item 3 in the CR list
bk8500.set_list_CR_param(ser,address,3,4.4,5.5)
bk8500.get_list_CR_param(ser,address,3)

#set the list name and read it back
bk8500.set_list_name(ser,address,"List 1")
bk8500.get_list_name(ser,address)

#save list file in slot 1 and reload it afterward
bk8500.store_list_file(ser,address,1)
bk8500.recall_list_file(ser,address,3)

#set memory partitioning for lists
bk8500.set_lists_partition(ser,address,1)
bk8500.get_lists_partition(ser,address)

#set control to local (panel) instead of remote
bk8500.set_remote(ser,address,False)

#disconnect serial port
ser.close()