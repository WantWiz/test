import os, math, re, json, csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
import plotly.express as px
from plotly.subplots import make_subplots
import seaborn as sns
import subprocess, sys
from pages import analyse_page
import Settings
import numpy as np
import time
from scipy import integrate

###################################################################
#                       CreateGraphError                       #
###################################################################
def CreateGraphError(Choice, Path, Err, Samples, ax, LowLeg):
    df = pd.read_csv(Path, sep='\t')

    if(Choice == "VHigh"):
        x_data_name = 'DMM VHigh (mV)'

        if(Err == "A"):
            ErrColName = "VHigh absolute error (mV)"
            Errm3stddevColName = "VHigh absolute error -3*std dev(mV)"
            Errp3stddevColName = "VHigh absolute error +3*std dev(mV)"

            GraphTitle = "VHigh measure absolute error (mV)"
            x_label = "VHigh multimeter measure (mV)"
            y_label = "VHigh measure absolute error (mV)"

        elif(Err == "R"):
            ErrColName = "VHigh relative error (%)"
            Errm3stddevColName = "VHigh -3*std dev relative error (%)"
            Errp3stddevColName = "VHigh +3*std dev relative error (%)"

            GraphTitle = "VHigh measure relative error (%)"
            x_label = "VHigh multimeter measure (mV)"
            y_label = "VHigh measure relative error (%)"

    elif(Choice == "IHigh"):
        x_data_name = "DMM IHigh (mA)"

        if(Err == "A"):
            ErrColName = "IHigh absolute error (mA)"
            Errm3stddevColName = "IHigh absolute error -3*std dev(mA)"
            Errp3stddevColName = "IHigh absolute error +3*std dev(mA)"

            GraphTitle = "IHigh measure absolute error (mA)"
            x_label = "IHigh multimeter measure (mA)"
            y_label = "IHigh measure absolute error (mA)"

        elif(Err == "R"):
            ErrColName = "IHigh relative error (%)"
            Errm3stddevColName = "IHigh -3*std dev relative error (%)"
            Errp3stddevColName = "IHigh +3*std dev relative error (%)"

            GraphTitle = "IHigh measure relative error (%)"
            x_label = "IHigh multimeter measure (mA)"
            y_label = "IHigh measure relative error (%)"

    elif(Choice == "VLow" ):
        x_data_name = 'DMM VLow (mV)'

        if(Err == "A"):
            if(LowLeg==1):
                ErrColName = "VLow1 absolute error (mV)"
                Errm3stddevColName = "VLow1 absolute error -3*std dev(mV)"
                Errp3stddevColName = "VLow1 absolute error +3*std dev(mV)"

                GraphTitle = "VLow1 measure absolute error (mV)"
                x_label = "VLow1 multimeter measure (mV)"
                y_label = "VLow1 measure absolute error (mV)"

            elif(LowLeg==2):
                ErrColName = "VLow2 absolute error (mV)"
                Errm3stddevColName = "VLow2 absolute error -3*std dev(mV)"
                Errp3stddevColName = "VLow2 absolute error +3*std dev(mV)"

                GraphTitle = "VLow2 measure absolute error (mV)"
                x_label = "VLow2 multimeter measure (mV)"
                y_label = "VLow2 measure absolute error (mV)"

        elif(Err == "R"):
            if(LowLeg==1):
                ErrColName = "VLow1 relative error (%)"
                Errm3stddevColName = "VLow1 -3*std dev relative error (%)"
                Errp3stddevColName = "VLow1 +3*std dev relative error (%)"

                GraphTitle = "VLow1 measure relative error (%)"
                x_label = "VLow1 multimeter measure (mV)"
                y_label = "VLow1 measure relative error (%)"

            if(LowLeg==2):
                ErrColName = "VLow2 relative error (%)"
                Errm3stddevColName = "VLow2 -3*std dev relative error (%)"
                Errp3stddevColName = "VLow2 +3*std dev relative error (%)"

                GraphTitle = "VLow2 measure relative error (%)"
                x_label = "VLow2 multimeter measure (mV)"
                y_label = "VLow2 measure relative error (%)"

    elif(Choice == "ILow" ):
        x_data_name = "DMM ILow (mA)"

        if(Err == "A"):
            if(LowLeg==1):
                ErrColName = 'ILow1 absolute error (mA)'
                Errm3stddevColName = "ILow1 absolute error -3*std dev(mA)"
                Errp3stddevColName = "ILow1 absolute error +3*std dev(mA)"

                GraphTitle = "ILow1 measure absolute error (mA)"
                x_label = "ILow1 multimeter measure (mA)"
                y_label = "ILow1 measure absolute error (mA)"

            elif(LowLeg==2):
                ErrColName = 'ILow2 absolute error (mA)'
                Errm3stddevColName = "ILow2 absolute error -3*std dev(mA)"
                Errp3stddevColName = "ILow2 absolute error +3*std dev(mA)"

                GraphTitle = "ILow2 measure absolute error (mA)"
                x_label = "ILow2 multimeter measure (mA)"
                y_label = "ILow2 measure absolute error (mA)"

        elif(Err == "R"):
            x_data_name = "DMM ILow (mA)"
            if(LowLeg==1):

                ErrColName = 'ILow1 relative error (%)'
                Errm3stddevColName = "ILow1 -3*std dev relative error (%)"
                Errp3stddevColName = "ILow1 +3*std dev relative error (%)"

                GraphTitle = "ILow1 measure relative error (%)"
                x_label = "ILow1 multimeter measure (mA)"
                y_label = "ILow1 measure relative error (%)"

            elif(LowLeg==2):
                ErrColName = 'ILow2 relative error (%)'
                Errm3stddevColName = "ILow2 -3*std dev relative error (%)"
                Errp3stddevColName = "ILow2 +3*std dev relative error (%)"

                GraphTitle = "ILow2 measure relative error (%)"
                x_label = "ILow2 multimeter measure (mA)"
                y_label = "ILow2 measure relative error (%)"

    Err_label = "Averaged : " + str(Samples) + " " + "samples"
    Errm3stddev_label = "Averaged - 3*standard deviation"
    Errp3stddev_label = "Averaged + 3*standard deviation"

    x_data = df[x_data_name]
    y_data1 = df[ErrColName]
    y_data2 = df[Errm3stddevColName]
    y_data3 = df[Errp3stddevColName]

    ax.plot(x_data, y_data1, label=Err_label)
    ax.plot(x_data, y_data2, label=Errm3stddev_label)
    ax.plot(x_data, y_data3, label=Errp3stddev_label)

    ax.tick_params(axis='x', labelsize=5)
    ax.tick_params(axis='y', labelsize=5)

    ax.set_title(GraphTitle, fontsize = 9)
    ax.set_xlabel(x_label, fontsize = 7)
    ax.set_ylabel(y_label, fontsize = 7)

    ax.legend(fontsize = 7)

###################################################################
#                     CreateGraphErrorSingle                      #
###################################################################
def CreateGraphErrorSingle(Choice, FilePath, Err, Samples, Display, LowLeg):

    LowLeg = int(LowLeg)

    df = pd.read_csv(FilePath, sep='\t')

    if(Choice == "VHigh"):
        x_data_name = 'DMM VHigh (mV)'

        if(Err == "A"):
            ErrColName = "VHigh absolute error (mV)"
            Errm3stddevColName = "VHigh absolute error -3*std dev(mV)"
            Errp3stddevColName = "VHigh absolute error +3*std dev(mV)"

            GraphTitle = "VHigh measure absolute error (mV)"
            x_label = "VHigh multimeter measure (mV)"
            y_label = "VHigh measure absolute error (mV)"

        elif(Err == "R"):
            ErrColName = "VHigh relative error (%)"
            Errm3stddevColName = "VHigh -3*std dev relative error (%)"
            Errp3stddevColName = "VHigh +3*std dev relative error (%)"

            GraphTitle = "VHigh measure relative error (%)"
            x_label = "VHigh multimeter measure (mV)"
            y_label = "VHigh measure relative error (%)"

    elif(Choice == "IHigh"):
        x_data_name = "DMM IHigh (mA)"

        if(Err == "A"):
            ErrColName = "IHigh absolute error (mA)"
            Errm3stddevColName = "IHigh absolute error -3*std dev(mA)"
            Errp3stddevColName = "IHigh absolute error +3*std dev(mA)"

            GraphTitle = "IHigh measure absolute error (mA)"
            x_label = "IHigh multimeter measure (mA)"
            y_label = "IHigh multimeter measure - IHigh TWIST measure (mA)"

        elif(Err == "R"):
            ErrColName = "IHigh relative error (%)"
            Errm3stddevColName = "IHigh -3*std dev relative error (%)"
            Errp3stddevColName = "IHigh +3*std dev relative error (%)"

            GraphTitle = "IHigh measure relative error (%)"
            x_label = "IHigh multimeter measure (mA)"
            y_label = "IHigh measure relative error (%)"

    elif(Choice == "VLow" ):
        x_data_name = 'DMM VLow (mV)'

        if(Err == "A"):
            if(LowLeg==1):
                ErrColName = "VLow1 absolute error (mV)"
                Errm3stddevColName = "VLow1 absolute error -3*std dev(mV)"
                Errp3stddevColName = "VLow1 absolute error +3*std dev(mV)"

                GraphTitle = "VLow1 measure absolute error (mV)"
                x_label = "VLow1 multimeter measure (mV)"
                y_label = "VLow1 measure absolute error (mV)"

            elif(LowLeg==2):
                ErrColName = "VLow2 absolute error (mV)"
                Errm3stddevColName = "VLow2 absolute error -3*std dev(mV)"
                Errp3stddevColName = "VLow2 absolute error +3*std dev(mV)"

                GraphTitle = "VLow2 measure absolute error (mV)"
                x_label = "VLow2 multimeter measure (mV)"
                y_label = "VLow2 measure absolute error (mV)"

        elif(Err == "R"):
            if(LowLeg==1):
                ErrColName = "VLow1 relative error (%)"
                Errm3stddevColName = "VLow1 -3*std dev relative error (%)"
                Errp3stddevColName = "VLow1 +3*std dev relative error (%)"

                GraphTitle = "VLow1 measure relative error (%)"
                x_label = "VLow1 multimeter measure (mV)"
                y_label = "VLow1 measure relative error (%)"

            if(LowLeg==2):
                ErrColName = "VLow2 relative error (%)"
                Errm3stddevColName = "VLow2 -3*std dev relative error (%)"
                Errp3stddevColName = "VLow2 +3*std dev relative error (%)"

                GraphTitle = "VLow2 measure relative error (%)"
                x_label = "VLow2 multimeter measure (mV)"
                y_label = "VLow2 measure relative error (%)"

    elif(Choice == "ILow" ):
        x_data_name = "DMM ILow (mA)"

        if(Err == "A"):
            if(LowLeg==1):
                ErrColName = 'ILow1 absolute error (mA)'
                Errm3stddevColName = "ILow1 absolute error -3*std dev(mA)"
                Errp3stddevColName = "ILow1 absolute error +3*std dev(mA)"

                GraphTitle = "ILow1 measure absolute error (mA)"
                x_label = "ILow1 multimeter measure (mA)"
                y_label = "ILow1 measure absolute error (mA)"

            elif(LowLeg==2):
                ErrColName = 'ILow2 absolute error (mA)'
                Errm3stddevColName = "ILow2 absolute error -3*std dev(mA)"
                Errp3stddevColName = "ILow2 absolute error +3*std dev(mA)"

                GraphTitle = "ILow2 measure absolute error (mA)"
                x_label = "ILow2 multimeter measure (mA)"
                y_label = "ILow2 measure absolute error (mA)"

        elif(Err == "R"):
            x_data_name = "DMM ILow (mA)"
            if(LowLeg==1):

                ErrColName = 'ILow1 relative error (%)'
                Errm3stddevColName = "ILow1 -3*std dev relative error (%)"
                Errp3stddevColName = "ILow1 +3*std dev relative error (%)"

                GraphTitle = "ILow1 measure relative error (%)"
                x_label = "ILow1 multimeter measure (mA)"
                y_label = "ILow1 measure relative error (%)"

            elif(LowLeg==2):
                ErrColName = 'ILow2 relative error (%)'
                Errm3stddevColName = "ILow2 -3*std dev relative error (%)"
                Errp3stddevColName = "ILow2 +3*std dev relative error (%)"

                GraphTitle = "ILow2 measure relative error (%)"
                x_label = "ILow2 multimeter measure (mA)"
                y_label = "ILow2 measure relative error (%)"

    Err_label = "Averaged : " + str(Samples) + " " + "samples"
    Errm3stddev_label = "Averaged - 3*standard deviation"
    Errp3stddev_label = "Averaged + 3*standard deviation"

    x_data = df[x_data_name]
    y_data1 = df[ErrColName]
    y_data2 = df[Errm3stddevColName]
    y_data3 = df[Errp3stddevColName]
    
    plt.plot(x_data, y_data1, label=Err_label)
    plt.plot(x_data, y_data2, label=Errm3stddev_label)
    plt.plot(x_data, y_data3, label=Errp3stddev_label)

    plt.tick_params(axis='x', labelsize=5)
    plt.tick_params(axis='y', labelsize=5)

    plt.suptitle(GraphTitle, fontsize = 9)
    plt.xlabel(x_label, fontsize = 7)
    plt.ylabel(y_label, fontsize = 7)

    plt.legend(fontsize = 7)

    FilePathNoExt = FilePath[:-4]
    PathToSaveFigSVG = FilePathNoExt + '_' + Err + "_" + Choice + '.svg'
    PathToSaveFigPNG = FilePathNoExt + '_' + Err + "_" + Choice + '.png'
    # fig = plt.figure(figsize=(8, 6))
    plt.savefig(PathToSaveFigSVG)
    plt.savefig(PathToSaveFigPNG)
    # if(Display == "Disp"):
    #     plt.show()
    # else:
    #     plt.clf()

##################################################################
#                   PlotAllAccuracyGraphs                        #
##################################################################
def PlotAllAccuracyGraphs(CSVResultsDict, NumberOfTWISTMeas, LowLeg):
    
    PathVhigh = CSVResultsDict["VHigh"]
    PathIHigh = CSVResultsDict["IHigh"]
    PathVlow = CSVResultsDict["VLow"]
    PathILow = CSVResultsDict["ILow"]

    PathToSaveFig = PathVhigh[:-15]
    
    fig1, axs1 = plt.subplots(nrows=2, ncols=2, figsize=(10, 8))

    CreateGraphError("VHigh", PathVhigh, "A", NumberOfTWISTMeas, axs1[0, 0], LowLeg)
    CreateGraphError("IHigh", PathIHigh, "A", NumberOfTWISTMeas, axs1[0, 1], LowLeg)
    CreateGraphError("VLow", PathVlow, "A", NumberOfTWISTMeas, axs1[1, 0], LowLeg)
    CreateGraphError("ILow", PathILow, "A", NumberOfTWISTMeas, axs1[1, 1], LowLeg)

    PathToSaveFigAbsSvg = PathToSaveFig + "_All_Abs.svg"
    PathToSaveFigAbsPng = PathToSaveFig + "_All_Abs.png"

    plt.savefig(PathToSaveFigAbsSvg)
    plt.savefig(PathToSaveFigAbsPng)
    # plt.show()

    fig2, axs2 = plt.subplots(nrows=2, ncols=2, figsize=(10, 8))
    CreateGraphError("VHigh", PathVhigh, "R", NumberOfTWISTMeas, axs2[0, 0], LowLeg)
    CreateGraphError("IHigh", PathIHigh, "R", NumberOfTWISTMeas, axs2[0, 1], LowLeg)
    CreateGraphError("VLow", PathVlow, "R", NumberOfTWISTMeas, axs2[1, 0], LowLeg)
    CreateGraphError("ILow", PathILow, "R", NumberOfTWISTMeas, axs2[1, 1], LowLeg)

    PathToSaveFigRelSvg = PathToSaveFig + "_All_Rel.svg"
    PathToSaveFigRelPng = PathToSaveFig + "_All_Rel.png"

    plt.savefig(PathToSaveFigRelSvg)
    plt.savefig(PathToSaveFigRelPng)
    # plt.show()

###################################################################
#                         CreateGraph2D                           #
###################################################################
def CreateGraph2D(ax, TestPathList, CurrentMin_mA, CurrentMax_mA, CenterILow_mA, LowLeg):

    for TestPath in TestPathList:

        TestNameNoCSV = os.path.basename(TestPath).replace('.csv', '')
        volt_match = re.findall(r'\d+V', TestNameNoCSV)
        lbl_volt_V = volt_match[0] if volt_match else ''

        data = pd.read_csv(TestPath, decimal=".", sep='\t')

        VLow_V = data['DMM VLow (mV)']/1000
        ILow_mA = data['DMM ILow (mA)']
        Eff_per = data['DMM Efficiency (%)']

        Filt_VLow_V = VLow_V[(ILow_mA >= CurrentMin_mA) & (ILow_mA <= CurrentMax_mA)]
        Filt_Eff_per = Eff_per[(ILow_mA >= CurrentMin_mA) & (ILow_mA <= CurrentMax_mA)]

        if(len(Filt_Eff_per)>1):#There is at least one data
            ax.scatter(Filt_VLow_V, Filt_Eff_per, label=lbl_volt_V, marker ='x')

    # Add x and y axis labels
    ax.set_xlabel('Vlow (V)')
    ax.set_ylabel('Efficiency (%)')

    # Add a legend
    ax.legend(fontsize=10)

    # Add a title
    Title = 'Efficiency vs VLow @ Ilow = '  + str(CenterILow_mA) + 'mA' + ", leg : " + str(LowLeg)
    # Title = "lol"
    ax.set_title(Title)
    ax.set_ylim(top=100)
    ax.grid()

###################################################################
#                       CreateGraph2DPowerErr                     #
###################################################################
def CreateGraph2DPowerErr(ax, TestPathList, CurrentMin_mA, CurrentMax_mA, CenterILow_mA, LowLeg):

    for TestPath in TestPathList:

        #Getting test voltage for legend label
        TestNameNoCSV = os.path.basename(TestPath).replace('.csv', '')
        volt_match = re.findall(r'\d+V', TestNameNoCSV)
        lbl_volt_V = volt_match[0] if volt_match else ''

        data = pd.read_csv(TestPath, decimal=".", sep='\t')

        VLow_V = data['DMM VLow (mV)']/1000
        ILow_mA = data['DMM ILow (mA)']
        Eff_per = data['DMM Efficiency (%)']

        Filt_VLow_V = VLow_V[(ILow_mA >= CurrentMin_mA) & (ILow_mA <= CurrentMax_mA)]
        Filt_Eff_per = Eff_per[(ILow_mA >= CurrentMin_mA) & (ILow_mA <= CurrentMax_mA)]

        if(len(Filt_Eff_per)>1):#There is at least one data
            ax.scatter(Filt_VLow_V, Filt_Eff_per, label=lbl_volt_V, marker ='x')

    # Add x and y axis labels
    ax.set_xlabel('Power DMM (W)')
    ax.set_ylabel('Efficiency (%)')

    # Add a legend
    ax.legend(fontsize=10)

    # Add a title
    Title = 'Efficiency vs VLow @ Ilow = '  + str(CenterILow_mA) + 'mA' + ", leg : " + str(LowLeg)
    # Title = "lol"
    ax.set_title(Title)
    ax.set_ylim(top=100)
    ax.grid()

###################################################################
#                      PlotPowerHighAbsError                      #
###################################################################
def PlotPowerHighAbsError(ax, TestsPathList, AverageCount):

    for TestPath in TestsPathList:
        
        #Getting test voltage for legend label
        TestNameNoCSV = os.path.basename(TestPath).replace('.csv', '')
        volt_match = re.findall(r'\d+V', TestNameNoCSV)
        lbl_volt_V = volt_match[0] if volt_match else ''

        data = pd.read_csv(TestPath, decimal=".", sep='\t')

        PowerHighDMM_W = data["DMM POWER High (W)"]
        Abs_Err_PowerHigh_W = data["Power High Absolute error (W)"] 

        ax.scatter(PowerHighDMM_W, Abs_Err_PowerHigh_W, label=lbl_volt_V, marker ='x')

    # Add x and y axis labels
    ax.set_xlabel('High side power DMM (W)')
    ax.set_ylabel('Absolute error on high side power measure (W)', fontsize = 8)

    # Add a legend
    ax.legend(fontsize=10)

    # Add a title
    Title = "Absolute error on high side power measure, average count : " + str(AverageCount)

    ax.set_title(Title, fontsize=8)
    # ax.set_ylim(top=100)
    ax.grid()

###################################################################
#                      PlotPowerHighRelError                      #
###################################################################
def PlotPowerHighRelError(ax, TestsPathList, AverageCount):
  
    for TestPath in TestsPathList:

        #Getting test voltage for legend label
        TestNameNoCSV = os.path.basename(TestPath).replace('.csv', '')
        volt_match = re.findall(r'\d+V', TestNameNoCSV)
        lbl_volt_V = volt_match[0] if volt_match else ''

        data = pd.read_csv(TestPath, decimal=".", sep='\t')

        PowerHighDMM_W = data["DMM POWER High (W)"]
        Rel_Err_PowerHigh_Per = data["Power High relative error (%)"] 

        ax.scatter(PowerHighDMM_W, Rel_Err_PowerHigh_Per, label=lbl_volt_V, marker ='x')

    # Add x and y axis labels
    ax.set_xlabel('High side power DMM (W)')
    ax.set_ylabel('Relative error on high side power measure (%)', fontsize = 8)

    # Add a legend
    ax.legend(fontsize=10)

    # Add a title
    Title = "Relative error on high side power measure, average count : " + str(AverageCount)

    ax.set_title(Title, fontsize = 8)
    # ax.set_ylim(top=100)
    ax.grid()

###################################################################
#                        PlotPowerLowAbsError                     #
###################################################################
def PlotPowerLowAbsError(ax, TestsPathList, AverageCount, LowLeg):
    
    LowLeg = int(LowLeg)

    for TestPath in TestsPathList:

        #Getting test voltage for legend label
        TestNameNoCSV = os.path.basename(TestPath).replace('.csv', '')
        volt_match = re.findall(r'\d+V', TestNameNoCSV)
        lbl_volt_V = volt_match[0] if volt_match else ''

        data = pd.read_csv(TestPath, decimal=".", sep='\t')

        DMMPowerLow_W = data["DMM POWER Low (W)"]
        
        if(LowLeg == 1):
            Abs_Err_PowerLow_Per = data["Power Low1 Absolute error (W)"]

        elif(LowLeg == 2):
            Abs_Err_PowerLow_Per = data["Power Low2 Absolute error (W)"]

        ax.scatter(DMMPowerLow_W, Abs_Err_PowerLow_Per, label=lbl_volt_V, marker ='x')

    # Add x and y axis labels
    ax.set_xlabel('Low side power DMM (W)')
    ax.set_ylabel("Absolute error on low side " + " " + str(LowLeg) +  "power measure (W)", fontsize = 8)

    # Add a legend
    ax.legend(fontsize=10)

    # Add a title
    Title = "Absolute error on low side" + str(LowLeg)+ "power measure, average count : " + str(AverageCount)

    ax.set_title(Title, fontsize = 8)
    # ax.set_ylim(top=100)
    ax.grid()

###################################################################
#                        PlotPowerLowRelError                     #
###################################################################
def PlotPowerLowRelError(ax, TestsPathList, AverageCount, LowLeg):
    
    LowLeg = int(LowLeg)

    for TestPath in TestsPathList:

        #Getting test voltage for legend label
        TestNameNoCSV = os.path.basename(TestPath).replace('.csv', '')
        volt_match = re.findall(r'\d+V', TestNameNoCSV)
        lbl_volt_V = volt_match[0] if volt_match else ''

        data = pd.read_csv(TestPath, decimal=".", sep='\t')

        DMMPowerLow_W = data["DMM POWER Low (W)"]
        
        if(LowLeg == 1):
            Abs_Err_PowerLow_Per = data["Power Low1 relative error (%)"]

        elif(LowLeg == 2):
            Abs_Err_PowerLow_Per = data["Power Low2 relative error (%)"]

        ax.scatter(DMMPowerLow_W, Abs_Err_PowerLow_Per, label=lbl_volt_V, marker ='x')

    # Add x and y axis labels
    ax.set_xlabel('Low side power DMM (W)')
    ax.set_ylabel("Relative error on low side " + str(LowLeg) +  " power measure (%)", fontsize = 8)

    # Add a legend
    ax.legend(fontsize=10)

    # Add a title
    Title = "Relative error on low side" + str(LowLeg)+ "power measure, average count : " + str(AverageCount)
    
    ax.set_title(Title, fontsize = 8)
    # ax.set_ylim(top=100)
    ax.grid()

###################################################################
#                        PlotPowerError                           #
###################################################################
def PlotPowerError(TestsPathList, LowLeg, AverageCount, Show):

    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    plt.subplots_adjust(hspace=0.6)  # adjust the hspace

    PlotPowerHighAbsError(ax[0,0], TestsPathList, AverageCount)
    PlotPowerHighRelError(ax[0,1], TestsPathList, AverageCount)

    PlotPowerLowAbsError(ax[1,0], TestsPathList, AverageCount, LowLeg)
    PlotPowerLowRelError(ax[1,1], TestsPathList, AverageCount, LowLeg)

    #Make Path
    DirPath = os.path.dirname(TestsPathList[0])
    TestName = os.path.basename(TestsPathList[0]).split('_')[0]

    TestNameFullPath = os.path.join(DirPath, TestName)

    PathToSaveFigSVG = TestNameFullPath + '_PowerError.svg'
    PathToSaveFigPNG = TestNameFullPath + '_PowerError.png'

    #Save
    plt.savefig(PathToSaveFigSVG)
    plt.savefig(PathToSaveFigPNG)

    if(Show == "Show"):
        os.startfile(PathToSaveFigSVG)

###################################################################
#                           PlotEff2D                             #
###################################################################
def PlotEff2D(TestsPathList, LowLeg, Show):

    CurrentDict = {
    "LowLimit_mA": [450, 1450 , 2450, 3450, 4450, 5450, 6450, 7450],
    "UpperLimit_mA": [550, 1550 , 2550, 3550, 4550, 5550, 6550, 7550],
    "Current_mA": [500, 1500 , 2500, 3500, 4500, 5500, 6500, 7500]
    }

    fig, ax = plt.subplots(3, 2, figsize=(10, 10))
    plt.subplots_adjust(hspace=0.6)  # adjust the hspace

    CreateGraph2D(ax[0,0], TestsPathList, CurrentDict["LowLimit_mA"][0], CurrentDict["UpperLimit_mA"][0], CurrentDict["Current_mA"][0], LowLeg)
    CreateGraph2D(ax[0,1], TestsPathList, CurrentDict["LowLimit_mA"][1], CurrentDict["UpperLimit_mA"][1], CurrentDict["Current_mA"][1], LowLeg)
    CreateGraph2D(ax[1,0], TestsPathList, CurrentDict["LowLimit_mA"][2], CurrentDict["UpperLimit_mA"][2], CurrentDict["Current_mA"][2], LowLeg)
    CreateGraph2D(ax[1,1], TestsPathList, CurrentDict["LowLimit_mA"][3], CurrentDict["UpperLimit_mA"][3], CurrentDict["Current_mA"][3], LowLeg)
    CreateGraph2D(ax[2,0], TestsPathList, CurrentDict["LowLimit_mA"][4], CurrentDict["UpperLimit_mA"][4], CurrentDict["Current_mA"][4], LowLeg)
    CreateGraph2D(ax[2,1], TestsPathList, CurrentDict["LowLimit_mA"][5], CurrentDict["UpperLimit_mA"][5], CurrentDict["Current_mA"][5], LowLeg)
    # CreateGraph2D(ax[3,0], TestsPathList, CurrentDict["LowLimit_mA"][6], CurrentDict["UpperLimit_mA"][6], CurrentDict["Current_mA"][6], LowLeg)
    # CreateGraph2D(ax[3,1], TestsPathList, CurrentDict["LowLimit_mA"][7], CurrentDict["UpperLimit_mA"][7], CurrentDict["Current_mA"][7], LowLeg)

    #Make Path
    DirPath = os.path.dirname(TestsPathList[0])
    TestName = os.path.basename(TestsPathList[0]).split('_')[0]

    TestNameFullPath = os.path.join(DirPath, TestName)
    PathToSaveFigSVG = TestNameFullPath + '_Eff2D.svg'
    PathToSaveFigPNG = TestNameFullPath + '_Eff2D.png'

    #Save
    plt.savefig(PathToSaveFigSVG)
    plt.savefig(PathToSaveFigPNG)

    # if(Show == "Show"):
    #     os.startfile(PathToSaveFigSVG)

###################################################################
#                           PlotEff3D                             #
###################################################################
def PlotEff3D(TestsPathList, LowLeg):

    Traces=[]#Initialise traces list
    i=0
    z=40 #We assume we will never have more than this different dataset to plot

    #List of 100 dark colors
    colors = ['#000000', '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#800000', '#008000',
                       '#000080', '#808000', '#800080', '#008080', '#C00000', '#00C000', '#0000C0', '#C0C000', '#C000C0',
                       '#00C0C0', '#400000', '#004000', '#000040', '#404000', '#400040', '#004040', '#200000', '#002000',
                       '#000020', '#202000', '#200020', '#002020', '#600000', '#006000', '#000060', '#606000', '#600060',
                       '#006060', '#A00000', '#00A000', '#0000A0', '#A0A000', '#A000A0', '#00A0A0', '#E00000', '#00E000',
                       '#0000E0', '#E0E000', '#E000E0', '#00E0E0']

    fig = plt.figure()

    for TestsPath in TestsPathList:
        i+=1
        z-=1

        #Getting test voltage for legend label
        TestNameNoCSV = os.path.basename(TestsPath).replace('.csv', '')
        volt_match = re.findall(r'\d+V', TestNameNoCSV)
        lbl_volt_V = volt_match[0] if volt_match else ''

        data = pd.read_csv(TestsPath, decimal=".", sep='\t')

        VLowDMM_V = data['DMM VLow (mV)']/1000
        ILowDMM_A = data['DMM ILow (mA)']/1000
        EffDMM_per = data['DMM Efficiency (%)']
        labelDMM = lbl_volt_V + " DMM" 

        if(LowLeg == 1):
            VLowTWIST_V = data['TWIST VLow1 (mV)']/1000
            ILowTWIST_A = data['TWIST ILow1 (mA)']/1000
            EffTWIST_per = data['TWIST Efficiency Leg 1 (%)']

        elif(LowLeg == 2):
            VLowTWIST_V = data['TWIST VLow2 (mV)']/1000
            ILowTWIST_A = data['TWIST ILow2 (mA)']/1000
            EffTWIST_per = data['TWIST Efficiency Leg 2 (%)']

        labelTWIST= lbl_volt_V + " TWIST"

        TraceiDMM = go.Scatter3d(x=VLowDMM_V, y=ILowDMM_A, z=EffDMM_per, mode='markers', marker=dict(color=colors[i], size=5), name=labelDMM)
        breakpoint()
        TraceiTWIST = go.Scatter3d(x=VLowTWIST_V, y=ILowTWIST_A, z=EffTWIST_per, mode='markers', marker=dict(color=colors[z], size=5), name=labelTWIST)

        Traces.append(TraceiDMM)
        Traces.append(TraceiTWIST)

    layout = go.Layout(scene=dict(xaxis_title='VLow (V)', yaxis_title='ILow (A)', zaxis_title='Efficiency (%)'),
                title='3D Scatter Plot')

    # Create a Figure object with the data and layout
    fig = go.Figure(data=Traces, layout=layout)

    #Make Path
    DirPath = os.path.dirname(TestsPathList[0])
    TestName = os.path.basename(TestsPathList[0]).split('_')[0]
    TestNameFullPath = os.path.join(DirPath, TestName)

    PathToSaveFig = TestNameFullPath + '_3d_plot.html'

    #Save and open
    pio.write_html(fig, PathToSaveFig, auto_open=False)


###################################################################
#                           PlotErr3D                             #
###################################################################
def PlotErr3D(TestsPathList, LowLeg, ErrorType):

    Traces=[]#Initialise traces list
    i=0
    z=40 #We assume we will never have more than this different dataset to plot

    #List of 100 dark colors
    colors = ['#000000', '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#800000', '#008000',
                       '#000080', '#808000', '#800080', '#008080', '#C00000', '#00C000', '#0000C0', '#C0C000', '#C000C0',
                       '#00C0C0', '#400000', '#004000', '#000040', '#404000', '#400040', '#004040', '#200000', '#002000',
                       '#000020', '#202000', '#200020', '#002020', '#600000', '#006000', '#000060', '#606000', '#600060',
                       '#006060', '#A00000', '#00A000', '#0000A0', '#A0A000', '#A000A0', '#00A0A0', '#E00000', '#00E000',
                       '#0000E0', '#E0E000', '#E000E0', '#00E0E0']

    fig = plt.figure()

    for TestsPath in TestsPathList:
        i+=1
        z-=1

        #Getting test voltage for legend label
        TestNameNoCSV = os.path.basename(TestsPath).replace('.csv', '')
        volt_match = re.findall(r'\d+V', TestNameNoCSV)
        lbl_volt_V = volt_match[0] if volt_match else ''

        data = pd.read_csv(TestsPath, decimal=".", sep='\t')

        if (ErrorType == "Abs"):
            if(LowLeg == 1):
                VLowTWIST_V = data['TWIST VLow1 (mV)']/1000
                ILowTWIST_A = data['TWIST ILow1 (mA)']/1000
                AbsErr_Per = data["Efficiency Absolute error leg 1 (%)"]

            elif(LowLeg == 2):
                VLowTWIST_V = data['TWIST VLow2 (mV)']/1000
                ILowTWIST_A = data['TWIST ILow2 (mA)']/1000
                AbsErr_Per = data["Efficiency Absolute error leg 2 (%)"]

        elif (ErrorType == "Rel"):
            if(LowLeg == 1):
                VLowTWIST_V = data['TWIST VLow1 (mV)']/1000
                ILowTWIST_A = data['TWIST ILow1 (mA)']/1000
                AbsErr_Per = data["Efficiency Relative error leg 1 (%)"]

            elif(LowLeg == 2):
                VLowTWIST_V = data['TWIST VLow2 (mV)']/1000
                ILowTWIST_A = data['TWIST ILow2 (mA)']/1000
                AbsErr_Per = data["Efficiency Relative error leg 2 (%)"]

        labelTWIST= lbl_volt_V 

        TraceiTWIST = go.Scatter3d(x=VLowTWIST_V, y=ILowTWIST_A, z=AbsErr_Per, mode='markers', marker=dict(color=colors[z], size=5), name=labelTWIST)
        Traces.append(TraceiTWIST)
        
    if (ErrorType == "Abs"):
        zaxisTitle = "Absolute error of eff measure (%)"

    elif (ErrorType == "Rel"):
        zaxisTitle = "Relative error of eff measure (%)"

    layout = go.Layout(scene=dict(xaxis_title='VLow (V)', yaxis_title='ILow (A)', zaxis_title=zaxisTitle),
                title='3D Scatter Plot')

    # Create a Figure object with the data and layout
    fig = go.Figure(data=Traces, layout=layout)

    #Make Path
    DirPath = os.path.dirname(TestsPathList[0])
    TestName = os.path.basename(TestsPathList[0]).split('_')[0]
    TestNameFullPath = os.path.join(DirPath, TestName)

    if (ErrorType == "Abs"):
        PathToSaveFig = TestNameFullPath + '_3d_abs_err.html'
    
    if (ErrorType == "Rel"):
        PathToSaveFig = TestNameFullPath + '_3d_rel_err.html'

    #Save and open
    pio.write_html(fig, PathToSaveFig, auto_open=False)


###################################################################
#                     PlotHistoDistrib                            #
###################################################################


HistNumberOfXAxisDivision = 100

def PlotHistoDistrib(CSVPath, Show, DutyCycleBinSize, my_plots):

    global HistNumberOfXAxisDivision
    
    df = pd.read_csv(CSVPath, delimiter='\t')
    
    # remove the colums that contains the values of DMM VHigh and duty cycle
    df = df.drop(df.columns[0], axis=1) 
    df = df.drop(df.columns[0], axis=1)
    # we put the columns in the best order for the display of the histograms
    df.iloc[:, [1, 2]] = df.iloc[:, [2, 1]].values
    df.iloc[:, [1, 3]] = df.iloc[:, [3, 1]].values
    column_names = df.columns.tolist()
    column_names[1], column_names[2] = column_names[2], column_names[1]
    column_names[1], column_names[3] = column_names[3], column_names[1]
    df.columns = column_names
    
    # calcul of mean value and Standart Deviation for each colums
    Settings.HistMeanStandardDeviationDict["VHigh (mV)"]["Mean"] = round(np.mean(df[column_names[0]]))
    Settings.HistMeanStandardDeviationDict["VHigh (mV)"]["StandartDeviation"] = round(np.std(df[column_names[0]]))
    Settings.HistMeanStandardDeviationDict["IHigh (mA)"]["Mean"] = round(np.mean(df[column_names[1]]))
    Settings.HistMeanStandardDeviationDict["IHigh (mA)"]["StandartDeviation"] = round(np.std(df[column_names[1]]))
    Settings.HistMeanStandardDeviationDict["VLow1 (mV)"]["Mean"] = round(np.mean(df[column_names[2]]))
    Settings.HistMeanStandardDeviationDict["VLow1 (mV)"]["StandartDeviation"] = round(np.std(df[column_names[2]]))
    Settings.HistMeanStandardDeviationDict["VLow2 (mV)"]["Mean"] = round(np.mean(df[column_names[3]]))
    Settings.HistMeanStandardDeviationDict["VLow2 (mV)"]["StandartDeviation"] = round(np.std(df[column_names[3]]))
    Settings.HistMeanStandardDeviationDict["ILow1 (mA)"]["Mean"] = round(np.mean(df[column_names[4]]))
    Settings.HistMeanStandardDeviationDict["ILow1 (mA)"]["StandartDeviation"] = round(np.std(df[column_names[4]]))
    Settings.HistMeanStandardDeviationDict["ILow2 (mA)"]["Mean"] = round(np.mean(df[column_names[5]]))
    Settings.HistMeanStandardDeviationDict["ILow2 (mA)"]["StandartDeviation"] = round(np.std(df[column_names[5]]))

    # Calculate number of rows and columns needed for subplots
    # n_cols = math.ceil(math.sqrt(len(df.columns)))
    n_cols = 2
    n_rows = math.ceil(len(df.columns) / n_cols)

    # Set size of figure and subplots
    fig = make_subplots(rows=n_rows, cols=n_cols, subplot_titles=df.columns, 
                        specs=[[{'type': 'histogram'}]*n_cols]*n_rows)

    # Plot statistical distribution of all columns
    for i, column in enumerate(df.columns):

        hist_values, hist_edges = np.histogram(df[column], bins=HistNumberOfXAxisDivision)

        max_samples_value = hist_values.max()

        mean = round(np.mean(df[column_names[i]]))
        std_deviation = round(np.std(df[column_names[i]]))

        x_gaussian = np.linspace(min(df[column_names[i]]), max(df[column_names[i]]), 1000)

        gaussian_values = (
            max_samples_value * np.exp(-0.5 * ((x_gaussian - mean) / std_deviation) ** 2)
        )

        row = i // n_cols + 1
        col = i % n_cols + 1

        fig.add_trace(go.Histogram(x=df[column], nbinsx=HistNumberOfXAxisDivision), row=row, col=col)
        fig.add_trace(go.Scatter(x=x_gaussian, y=gaussian_values, mode="lines", line=dict(color="red")), row=row, col=col)

    # Set layout and style
    fig.update_layout(
        height=None, 
        width=None,
        showlegend=False,
        xaxis={'title': ''},
        yaxis={'title': ''}
    )

    PNGPath = os.path.dirname(CSVPath)
    PNGPath = os.path.join(PNGPath, "Histograms_" + str(Settings.JsonTestsHistory_data["TestNamesHistory"][analyse_page.TestIndex]) + ".png")
    fig.write_image(PNGPath)

    #Make Path
    PathToSaveFigSVG = CSVPath.replace('.csv', '_Histo.svg')

    my_plots["title"].append("Histograms of raw datasets from " + str(Settings.JsonTestsHistory_data["TestNamesHistory"][analyse_page.TestIndex]) + " on LEG " + str(Settings.JsonTestsHistory_data["LowLegHistory"][analyse_page.TestIndex]))
    my_plots["fig"].append(fig)
    my_plots["zMin"].append(0)
    my_plots["zMax"].append(100)

    return my_plots


###################################################################
#                PlotHistoDistrib Coeffs History                  #
###################################################################

def PlotHistoDistribCoeffsHistory(CSVPath, Show, DutyCycleBinSize, my_plots):

    df = pd.read_csv(CSVPath, delimiter='\t', encoding='latin-1')
    # remove the columns that contains correlation coeffs; BoardSN and the unused leg
    df = df.drop(df.columns[0], axis=1)
    df = df.drop(df.columns[2], axis=1)
    df = df.drop(df.columns[4], axis=1)
    df = df.drop(df.columns[6], axis=1)
    df = df.drop(df.columns[8], axis=1)
    df = df.drop(df.columns[10], axis=1)
    df = df.drop(df.columns[12], axis=1)

    column_names = df.columns.tolist()

    # calcul of mean value and Standart Deviation for each colums
    for key, column_name in zip(Settings.CoeffsHistoryMeanStandardDeviationDict.keys(), column_names):
        if "G" in key:
            Settings.CoeffsHistoryMeanStandardDeviationDict[key]["Mean"] = round(np.mean(df[column_name][(df[column_name] != 1) & (df[column_name] != 0)]), 2)
            Settings.CoeffsHistoryMeanStandardDeviationDict[key]["StandartDeviation"] = round(np.std(df[column_name][(df[column_name] != 1) & (df[column_name] != 0)]), 2)
        else:
            Settings.CoeffsHistoryMeanStandardDeviationDict[key]["Mean"] = round(np.mean(df[column_name][(df[column_name] != 1) & (df[column_name] != 0)]))
            Settings.CoeffsHistoryMeanStandardDeviationDict[key]["StandartDeviation"] = round(np.std(df[column_name][(df[column_name] != 1) & (df[column_name] != 0)]))
    
    # Calculate number of rows and columns needed for subplots
    # n_cols = math.ceil(math.sqrt(len(df.columns)))
    n_cols = 2
    n_rows = math.ceil(len(df.columns) / n_cols)

    # Set size of figure and subplots
    fig = make_subplots(rows=n_rows, cols=n_cols, subplot_titles=df.columns, 
                        specs=[[{'type': 'histogram'}]*n_cols]*n_rows)

    # Plot statistical distribution of all columns
    for i, column in enumerate(df.columns):
        if i in [0,1,2,3,6,7,8,9]:
            df[column] = df[column][(df[column] != 1) & (df[column] != 0)]
        row = i // n_cols + 1
        col = i % n_cols + 1

        column_values = df[column].dropna()
        coeffs_history_values, hist_edges = np.histogram(column_values, bins=20)

        max_samples_value = coeffs_history_values.max()
        mean = Settings.CoeffsHistoryMeanStandardDeviationDict[column]["Mean"]
        std_deviation = Settings.CoeffsHistoryMeanStandardDeviationDict[column]["StandartDeviation"]
        x_gaussian = np.linspace(min(column_values), max(column_values), 1000)

        gaussian_values = (
            max_samples_value * np.exp(-0.5 * ((x_gaussian - mean) / std_deviation) ** 2)
        )
        row = i // n_cols + 1
        col = i % n_cols + 1

        fig.add_trace(go.Histogram(x=df[column], nbinsx=50), row=row, col=col)
        fig.add_trace(go.Scatter(x=x_gaussian, y=gaussian_values, mode="lines", line=dict(color="red")), row=row, col=col)

    # Set layout and style
    fig.update_layout(
        height=None, 
        width=None,
        showlegend=False,
        xaxis={'title': ''},
        yaxis={'title': ''}
    )

    my_plots["title"].append("Histograms of calibration coefficients")
    my_plots["fig"].append(fig)
    my_plots["zMin"].append(0)
    my_plots["zMax"].append(100)

    return my_plots



###################################################################
#                PlotHistoDistrib Histo History                   #
###################################################################

def PlotHistoDistribHistoHistory(CSVPath, Show, DutyCycleBinSize, my_plots):

    df = pd.read_csv(CSVPath, delimiter='\t', encoding='latin-1')
    column_names = df.columns.tolist()

    if "LEG_1" in CSVPath:
        DictName = Settings.HistoHistoryMeanStandardDeviationDictLeg1
        LowLeg = "1"
    else:
        DictName = Settings.HistoHistoryMeanStandardDeviationDictLeg2
        LowLeg = "2"

    # calcul of mean value and Standart Deviation for each colums
    for key, column_name in zip(DictName.keys(), column_names):
        DictName[key]["Mean"] = round(np.mean(df[column_name]))
        DictName[key]["StandartDeviation"] = round(np.std(df[column_name]))
    
    # Calculate number of rows and columns needed for subplots
    # n_cols = math.ceil(math.sqrt(len(df.columns)))
    n_cols = 2
    n_rows = math.ceil(len(df.columns) / n_cols)

    # Set size of figure and subplots
    fig = make_subplots(rows=n_rows, cols=n_cols, subplot_titles=df.columns, 
                        specs=[[{'type': 'histogram'}]*n_cols]*n_rows)

    # Plot statistical distribution of all columns
    for i, column in enumerate(df.columns):

        # if "Mean" in column:
        #     column_DictName = column.replace("_Mean", "")
        # else:
        #     column_DictName = column.replace("_StandartDeviation", "")
        row = i // n_cols + 1
        col = i % n_cols + 1

        histo_history_values, hist_edges = np.histogram(df[column], bins=20)

        max_samples_value = histo_history_values.max()


        mean = DictName[column]["Mean"]
        std_deviation = DictName[column]["StandartDeviation"]
        x_gaussian = np.linspace(min(df[column]), max(df[column]), 1000)

        gaussian_values = (
            max_samples_value * np.exp(-0.5 * ((x_gaussian - mean) / std_deviation) ** 2)
        )
        row = i // n_cols + 1
        col = i % n_cols + 1
        fig.add_trace(go.Histogram(x=df[column], nbinsx=50), row=row, col=col)
        fig.add_trace(go.Scatter(x=x_gaussian, y=gaussian_values, mode="lines", line=dict(color="red")), row=row, col=col)

    # Set layout and style
    fig.update_layout(
        height=None, 
        width=None,
        showlegend=False,
        xaxis={'title': ''},
        yaxis={'title': ''}
    )

    my_plots["title"].append("Histograms of histogram test mean values and standart deviation for each measure on LEG " + LowLeg)
    my_plots["fig"].append(fig)
    my_plots["zMin"].append(0)
    my_plots["zMax"].append(100)

    return my_plots
