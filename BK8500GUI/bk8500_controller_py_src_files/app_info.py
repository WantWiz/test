# Static information used in the code such as menu items lists are included in this file as well
from threading import Timer
import sys
import serial
import glob

class RepeatableTimer(object):
    def __init__(self, interval, function, args=[], kwargs={}):
        self._interval = interval
        self._function = function
        self._args = args
        self._kwargs = kwargs
    def start(self):
        t = Timer(self._interval, self._function, *self._args, **self._kwargs)
        t.start()

# Taken from StackOverflow, find available serial ports:
def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    if len(result)==0:
        result.append("")
    return result

def super_print(widget):
    '''filename is the file where output will be written'''
    def wrap(func):
        '''func is the function you are "overriding", i.e. wrapping'''
        def wrapped_func(*args,**kwargs):
            '''*args and **kwargs are the arguments supplied
            to the overridden function'''
            #use with statement to open, write to, and close the file safely
            widget.insert("1.0", "\n")
            widget.insert("1.0",*args,**kwargs)
            #now original function executed with its arguments as normal
            return func(*args,**kwargs)
        return wrapped_func
    return wrap

Models_list = {
    "8500": "120V, 30A, 300W",
    "8502": "500V, 15A, 300W",
    "8510": "120V, 120A, 600W",
    "8512": "500V, 30A, 600W",
    "8514": "120V, 240A, 1200W",
    "8518": "60V, 240A, 1200W",
    "8520": "120V, 240A, 2400W",
    "8522": "500V, 120A, 2400W",
    "8524": "60V, 240A, 5000W",
    "8526": "500V, 120A, 5000W",
}

# Static info for GUI items
# define all defaults of drop-down items in the app window:
opt_ser_baud = [
    2400,
    4800,
    9600,
    19200,
    38400
]

opt_ser_parity = [
    "none",
    "even",
    "odd"
]

opt_ser_ports = [""]

opt_tran_op = [
    "Continuous",
    "Pulse",
    "Toggled"
]

op_setting_slot = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25
]