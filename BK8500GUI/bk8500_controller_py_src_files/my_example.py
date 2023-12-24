import bk8500
import serial

address = 0
ser = serial.Serial()
ser.baudrate = 9600
ser.port = 'COM20'
ser.parity = 'N'
ser.timeout = 2
print(ser)
ser.open()
print(ser.is_open)

#set remote
bk8500.set_remote(ser,address,True)

#enable input
bk8500.enable_input(ser,address,True)

#set current
bk8500.set_current(ser,address,2)