import time

class EAPSI9750:
    def __init__(self, ress):
        self.ress = ress
        ress.write("*CLS")

    def exit(self):
        self.ress.write('SOURce:VOLTage 20')
        time.sleep(0.5)
        self.ress.write('OUTput OFF')
        self.ress.write('SYST:LOCK OFF')

    def init(self):
        self.ress.write('SYST:LOCK ON')
        time.sleep(0.5)
        self.ress.write('SOURce:VOLTage 20')
        time.sleep(0.5)
        self.ress.write('OUTput ON')
        time.sleep(1)

    def setVoltage_mV(self, Voltage_mV):
        Voltage_V = round(Voltage_mV/1000,0)
        Voltage_V = str(Voltage_V)
        Msg = 'SOURce:VOLTage ' + Voltage_V
        self.ress.write(Msg)

    def setVoltage_V(self, Voltage_V):
        Voltage_V = str(Voltage_V)
        Msg = 'SOURce:VOLTage ' + Voltage_V
        self.ress.write(Msg)

    def exit(self):
        self.ress.write('SOURce:VOLTage 20')
        time.sleep(0.5)
        self.ress.write('OUTput OFF')
        self.ress.write('SYST:LOCK OFF')