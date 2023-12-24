import os, csv, pandas as pd, math

###################################################################
#                          SaveHeader                             #
###################################################################
def SaveHeader(Path, Header):

    with open(Path, 'w', newline='', encoding='UTF8') as file:
        writer = csv.writer(file, delimiter= '\t')
        writer.writerow(Header)

###################################################################
#                           SaveHeaderAcc                         #
###################################################################
def SaveHeaderAcc(Choice, FilePath, HeaderDict):
    global file, writer

    if(Choice == "VHigh"):
        Header = HeaderDict["VHigh"]
    elif(Choice == "IHigh"):
        Header = HeaderDict["IHigh"]
    elif(Choice == "VLow"):
        Header = HeaderDict["VLow"]
    elif(Choice == "ILow"):
        Header = HeaderDict["ILow"]

    with open(FilePath, 'w', newline='', encoding='UTF8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(Header)

###################################################################
#                         ComputeTWISTEff                         #
###################################################################
def ComputeTWISTEff(FilePath):
    
    mVmAToWConversionRatio = 1e-6

    df = pd.read_csv(FilePath, sep='\t')

    #GetData
    VHigh_mV = df["TWIST VHigh (mV)"]
    IHigh_mA = df["TWIST IHigh (mA)"]
    VLow1_mV = df["TWIST VLow1 (mV)"]
    VLow2_mV = df["TWIST VLow2 (mV)"]
    ILow1_mA = df["TWIST ILow1 (mA)"]
    ILow2_mA = df["TWIST ILow2 (mA)"]


    #Compute
    PowerHigh_W = round(VHigh_mV*IHigh_mA*mVmAToWConversionRatio, 1)
    PowerLow1_W = round(VLow1_mV*ILow1_mA*mVmAToWConversionRatio, 1)
    PowerLow2_W = round(VLow2_mV*ILow2_mA*mVmAToWConversionRatio, 1)

    if (PowerHigh_W == 0).any():
        PowerHigh_W[PowerHigh_W == 0] = 0.01

    Eff_leg1_Per = (PowerLow1_W/PowerHigh_W)*100
    Eff_leg2_Per = (PowerLow2_W/PowerHigh_W)*100
    Eff_leg1_Per = round(Eff_leg1_Per, 1)
    Eff_leg2_Per = round(Eff_leg2_Per, 1)

    #Write back to csv
    df["TWIST Power High (W)"] = PowerHigh_W
    df["TWIST Power Leg 1 (W)"] = PowerLow1_W
    df["TWIST Power Leg 2 (W)"] = PowerLow2_W
    df["TWIST Efficiency Leg 1 (%)"] = Eff_leg1_Per
    df["TWIST Efficiency Leg 2 (%)"] = Eff_leg2_Per

    # Save the updated CSV file
    df.to_csv(FilePath, index=False, sep='\t')

###################################################################
#                       ComputeTWISTPowerErr                      #
###################################################################
def ComputeTWISTPowerErr(FilePath):
    df = pd.read_csv(FilePath, sep='\t')

    #GetData
    TWISTPowerHigh_W = df["TWIST Power High (W)"]
    TWISTPowerLow1_W = df["TWIST Power Leg 1 (W)"]
    TWISTPowerLow2_W = df["TWIST Power Leg 2 (W)"]
    DMMPowerHigh_W = df["DMM POWER High (W)"]
    DMMPowerLow_W = df["DMM POWER Low (W)"]

    if (DMMPowerHigh_W == 0).any():
        DMMPowerHigh_W[DMMPowerHigh_W == 0] = 0.01

    #Compute
    Abs_Err_PowerHigh_W = round(DMMPowerHigh_W-TWISTPowerHigh_W, 1)
    Abs_Err_Power_Low1_W = round(DMMPowerLow_W-TWISTPowerLow1_W, 1)
    Abs_Err_Power_Low2_W = round(DMMPowerLow_W-TWISTPowerLow2_W, 1)

    Rel_Err_PowerHigh_Per = (Abs_Err_PowerHigh_W/DMMPowerHigh_W)*100
    Rel_Err_PowerHigh_Per = round(Rel_Err_PowerHigh_Per, 0)
    Rel_Err_PowerLow1_Per = (Abs_Err_Power_Low1_W/DMMPowerLow_W)*100
    Rel_Err_PowerLow1_Per = round(Rel_Err_PowerLow1_Per, 0)
    Rel_Err_PowerLow2_Per = (Abs_Err_Power_Low2_W/DMMPowerLow_W)*100
    Rel_Err_PowerLow2_Per = round(Rel_Err_PowerLow2_Per, 0)

    #Write back to csv
    df["Power High Absolute error (W)"] = Abs_Err_PowerHigh_W
    df["Power Low1 Absolute error (W)"] = Abs_Err_Power_Low1_W
    df["Power Low2 Absolute error (W)"] = Abs_Err_Power_Low2_W

    df["Power High relative error (%)"] = Rel_Err_PowerHigh_Per
    df["Power Low1 relative error (%)"] = Rel_Err_PowerLow1_Per
    df["Power Low2 relative error (%)"] = Rel_Err_PowerLow2_Per

    # Save the updated CSV file
    df.to_csv(FilePath, index=False, sep='\t')

###################################################################
#                       ComputeTWISTEffErr                        #
###################################################################
def ComputeTWISTEffErr(FilePath):
    
    df = pd.read_csv(FilePath, sep='\t')

    #GetData
    Eff_leg1_Per= df["TWIST Efficiency Leg 1 (%)"]
    Eff_leg2_Per= df["TWIST Efficiency Leg 2 (%)"]
    DMM_Eff_Per = df["DMM Efficiency (%)"]

    if (DMM_Eff_Per == 0).any():
        DMM_Eff_Per[DMM_Eff_Per == 0] = 0.01

    #Compute
    Abs_Err_Leg1 = round(Eff_leg1_Per-DMM_Eff_Per, 1)
    Abs_Err_Leg2 = round(Eff_leg2_Per-DMM_Eff_Per, 1)
    Rel_Err_Leg1 = round(Abs_Err_Leg1/DMM_Eff_Per, 1)
    Rel_Err_Leg2 = round(Abs_Err_Leg2/DMM_Eff_Per, 1)

    #Write back to csv
    df["Efficiency Absolute error leg 1 (%)"] = Abs_Err_Leg1
    df["Efficiency Absolute error leg 2 (%)"] = Abs_Err_Leg2
    df["Efficiency Relative error leg 1 (%)"] = Rel_Err_Leg1
    df["Efficiency Relative error leg 2 (%)"] = Rel_Err_Leg2

    # Save the updated CSV file
    df.to_csv(FilePath, index=False, sep='\t')

###################################################################
#                          AverageBlock                           #
###################################################################
def AverageBlock(InputFilePath, block_size):

    OutputFilePath = InputFilePath.replace('.csv', 'AVGD.csv')

    with open(InputFilePath, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        headers = next(reader)
        n_columns = len(headers)
        data = [row for row in reader]

    n_rows = len(data)
    n_blocks = n_rows // block_size
    averages = [[0.0 for i in range(n_columns)] for j in range(n_blocks)]
    std_devs = [0.0 for i in range(n_blocks)]

    for i in range(n_rows):
        block = i // block_size
        for j in range(n_columns):
            averages[block][j] += float(data[i][j])

    for i in range(n_blocks):
        for j in range(n_columns):
            averages[i][j] /= block_size
            averages[i][j] = round(averages[i][j], 2)

    with open(OutputFilePath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        writer.writerow(headers)
        for i in range(n_blocks):
            averages[i].append(std_devs[i])
            writer.writerow(averages[i])

    return OutputFilePath

###################################################################
#                   AverageBlockAndStdDev                         #
###################################################################
def AverageBlockAndStdDev(InputFilePath, block_size):

    OutputFilePath = InputFilePath.replace('.csv', '_AVGD.csv')

    with open(InputFilePath, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        headers = next(reader)
        n_columns = len(headers)
        data = [list(map(float, row)) for row in reader]

    n_rows = len(data)
    n_blocks = n_rows // block_size
    averages = [[0.0 for i in range(n_columns)] for j in range(n_blocks)]
    std_devs = [[0.0 for i in range(n_columns)] for j in range(n_blocks)]

    for i in range(n_rows):
        block = i // block_size
        for j in range(n_columns):
            averages[block][j] += data[i][j]

    for i in range(n_blocks):
        for j in range(n_columns):
            averages[i][j] /= block_size
            std_dev = math.sqrt(sum((data[k][j] - averages[i][j]) ** 2 for k in range(i * block_size, (i + 1) * block_size)) / block_size)
            std_devs[i][j] = round(std_dev, 2)

    output_headers = []
    for header in headers:
        output_headers.append(header)
        output_headers.append(f"{header}_stddev")
    
    output_data = []
    for i in range(n_blocks):
        row = []
        for j in range(n_columns):
            row.append(round(averages[i][j], 2))
            row.append(std_devs[i][j])
        output_data.append(row)

    with open(OutputFilePath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        writer.writerow(output_headers)
        for row in output_data:
            writer.writerow(row)

    return OutputFilePath

###################################################################
#                      ComputeAndSaveErrors                       #
###################################################################
def ComputeAndSaveErrors(Choice, FilePath, LowLeg):

    LowLeg = int(LowLeg)

    unit = '(mA)'
    if(Choice == "VLow" or Choice == "VHigh"):
        unit = '(mV)'

    #Column names
    AbsErr = Choice + str(LowLeg) + 'abs error' + unit
    AbsErrm3stddev = Choice + ' abs error - 3 sigma ' + unit
    AbsErrp3stddev = Choice + ' abs error + 3 sigma ' + unit
    RelErr = Choice + str(LowLeg) +'relative error (%)'
    RelErrm3stddev = Choice + ' rel error - 3 sigma'
    RelErrp3stddev = Choice + ' rel error + 3 sigma'

    #Get Data
    if(Choice == "VHigh"):
        ValueDMMColName = 'DMM VHigh (mV)'
        ValueTwistColName = "TWIST VHigh (mV)"
        StdDevColName = "TWIST VHigh (mV)_stddev"

        AbsErrColName = "VHigh absolute error (mV)"
        AbsErrm3stddevColName = "VHigh absolute error -3*std dev(mV)"
        AbsErrp3stddevColName = "VHigh absolute error +3*std dev(mV)"
        RelErrColName = "VHigh relative error (%)"
        RelErrm3stddevColName = "VHigh -3*std dev relative error (%)"
        RelErrp3stddevColName = "VHigh +3*std dev relative error (%)"
    
    elif(Choice == "IHigh"):
        ValueDMMColName = "DMM IHigh (mA)"
        ValueTwistColName = "TWIST IHigh (mA)"
        StdDevColName = "TWIST IHigh (mA)_stddev"

        AbsErrColName = "IHigh absolute error (mA)"
        AbsErrm3stddevColName = "IHigh absolute error -3*std dev(mA)"
        AbsErrp3stddevColName = "IHigh absolute error +3*std dev(mA)"
        RelErrColName = "IHigh relative error (%)"
        RelErrm3stddevColName = "IHigh -3*std dev relative error (%)"
        RelErrp3stddevColName = "IHigh +3*std dev relative error (%)"

    elif(Choice == "VLow"):
        ValueDMMColName = 'DMM VLow (mV)'

        if(LowLeg == 1):
            ValueTwistColName = 'TWIST VLow1 (mV)'
            StdDevColName = 'TWIST VLow1 (mV)_stddev'

            AbsErrColName = "VLow1 absolute error (mV)"
            AbsErrm3stddevColName = "VLow1 absolute error -3*std dev(mV)"
            AbsErrp3stddevColName = "VLow1 absolute error +3*std dev(mV)"
            RelErrColName = "VLow1 relative error (%)"
            RelErrm3stddevColName = "VLow1 -3*std dev relative error (%)"
            RelErrp3stddevColName = "VLow1 +3*std dev relative error (%)"

        elif(LowLeg == 2):
            ValueTwistColName = 'TWIST VLow2 (mV)'
            StdDevColName = 'TWIST VLow2 (mV)_stddev'

            AbsErrColName = "VLow2 absolute error (mV)"
            AbsErrm3stddevColName = "VLow2 absolute error -3*std dev(mV)"
            AbsErrp3stddevColName = "VLow2 absolute error +3*std dev(mV)"
            RelErrColName = "VLow2 relative error (%)"
            RelErrm3stddevColName = "VLow2 -3*std dev relative error (%)"
            RelErrp3stddevColName = "VLow2 +3*std dev relative error (%)"

    elif(Choice == "ILow"):
        ValueDMMColName = "DMM ILow (mA)"

        if(LowLeg == 1):
            ValueTwistColName = "TWIST ILow1 (mA)"
            StdDevColName = "TWIST ILow1 (mA)_stddev"

            AbsErrColName = "ILow1 absolute error (mA)"
            AbsErrm3stddevColName = "ILow1 absolute error -3*std dev(mA)"
            AbsErrp3stddevColName = "ILow1 absolute error +3*std dev(mA)"
            RelErrColName = "ILow1 relative error (%)"
            RelErrm3stddevColName = "ILow1 -3*std dev relative error (%)"
            RelErrp3stddevColName = "ILow1 +3*std dev relative error (%)"

        elif(LowLeg == 2):
            ValueTwistColName = "TWIST ILow2 (mA)"
            StdDevColName = "TWIST ILow2 (mA)_stddev"

            AbsErrColName = "ILow2 absolute error (mA)"
            AbsErrm3stddevColName = "ILow2 absolute error -3*std dev(mA)"
            AbsErrp3stddevColName = "ILow2 absolute error +3*std dev(mA)"
            RelErrColName = "ILow2 relative error (%)"
            RelErrm3stddevColName = "ILow2 -3*std dev relative error (%)"
            RelErrp3stddevColName = "ILow2 +3*std dev relative error (%)"

    df = pd.read_csv(FilePath, sep='\t')
    
    ValueDMM = df[ValueDMMColName]
    ValueTwist = df[ValueTwistColName]
    StdDev = df[StdDevColName]

    # Add the error columns
    AbsErr = round(ValueDMM - ValueTwist, 0)
    AbsErrm3stddev = round(AbsErr - 3*StdDev,0)
    AbsErrp3stddev = round(AbsErr + 3*StdDev,0)
    RelErr = round(((AbsErr/ValueDMM)*100), 1)
    RelErrm3stddev = round(((AbsErrm3stddev/ValueDMM)*100), 1)
    RelErrp3stddev = round(((AbsErrp3stddev/ValueDMM)*100), 1)

    df[AbsErrColName] = AbsErr
    df[AbsErrm3stddevColName] = AbsErrm3stddev
    df[AbsErrp3stddevColName] = AbsErrp3stddev
    df[RelErrColName] = RelErr
    df[RelErrm3stddevColName] = RelErrm3stddev
    df[RelErrp3stddevColName] = RelErrp3stddev

    # Save the updated CSV file
    df.to_csv(FilePath, index=False, sep='\t')