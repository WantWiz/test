###################################################################
#                    ShuntVoltage_mVToCurr_mA                     #
###################################################################
def ShuntVoltage_mVToCurr_mA(Voltage_mV, shunt_in_milliohm, CorrectionRatio):
    
    current_mA = (abs(Voltage_mV/(shunt_in_milliohm/1000))*CorrectionRatio)
    current_mA = round(current_mA, 0)

    return current_mA

###################################################################
#                     ComputePowerInWatt                          #
###################################################################
def ComputePowerInWatt(Voltage_in_Volt, Current_in_AMP):

    Power_W = Voltage_in_Volt*Current_in_AMP
    Power_W = round(Power_W,1)

    return(Power_W)

###################################################################
#                       ComputeEff_Per                            #
###################################################################
def ComputeEff_Per(PLow_W, PHigh_W):
        
    if (PHigh_W==0):
        PHigh_W=9999#To avoid null division error

    Eff = PLow_W/PHigh_W
    Eff_Per = round((Eff*100), 1)

    return Eff_Per

###################################################################
#                     ComputePowerResults                         #
###################################################################
def ComputePowerResults(DataDMM):
    
    #initialize power array
    PowerList_W = [0]*3

    VHigh_V = DataDMM[0]/1000
    IHigh_A = DataDMM[1]/1000
    VLow_V = DataDMM[2]/1000
    ILow_A = DataDMM[3]/1000

    #Compute power from voltage and current
    PowerHigh_W=ComputePowerInWatt(VHigh_V, IHigh_A)
    PowerLow_W=ComputePowerInWatt(VLow_V, ILow_A)

    #Compute efficiency
    Efficiency_Per = ComputeEff_Per(PowerLow_W, PowerHigh_W)

    PowerList_W[0] = PowerHigh_W
    PowerList_W[1] = PowerLow_W
    PowerList_W[2] = Efficiency_Per

    return PowerList_W