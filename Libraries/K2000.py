import ssl
import time
import pyvisa

class KEITHLEY2000:
    def __init__(self, ress):
        self.ress = ress
        ress.write("*rst; status:preset; *cls")

    def getAveragedVoltage_mV(self,number_of_readings, interval_in_ms):

        Value=0
        Avg_Value=0

        self.ress.write("status:measurement:enable 512; *sre 1")
        self.ress.write("sample:count %d" % number_of_readings)
        self.ress.write("trigger:source bus")
        self.ress.write("trigger:delay %f" % (interval_in_ms / 1000.0))
        self.ress.write("trace:points %d" % number_of_readings)
        self.ress.write("trace:feed sense1; feed:control next")

        self.ress.write("initiate")
        self.ress.assert_trigger()
        self.ress.wait_for_srq()

        Value = self.ress.query_ascii_values("trace:data?")
        Avg_Value = (sum(Value) / len(Value))
        Avg_Value_mV = Avg_Value*1000
        Avg_Value_mV = Avg_Value_mV

        self.ress.query("status:measurement?")
        self.ress.write("trace:clear; feed:control next")

        return Avg_Value_mV