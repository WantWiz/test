import os, math, re, dash
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
import seaborn as sns
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import plotly.express as px
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output

###################################################################
#                       InteractivePlotEff3D                      #
###################################################################
def InteractivePlotEff3D(TestsPathList, LowLeg, my_plots):
    title="Efficiency function of output voltage and output current"
    Traces=[]#Initialise traces list
    i=0
    z=40 #We assume we will never have more than this different dataset to plot

    #List of 40 dark colors
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

        TraceiDMM = go.Surface(x=VLowDMM_V, y=ILowDMM_A, z=EffDMM_per, name=labelDMM)
        # TraceiDMM = go.Scatter3d(x=VLowDMM_V, y=ILowDMM_A, z=EffDMM_per, mode='markers', marker=dict(color=colors[i], size=5), name=labelDMM)
        TraceiTWIST = go.Scatter3d(x=VLowTWIST_V, y=ILowTWIST_A, z=EffTWIST_per, mode='markers', marker=dict(color=colors[z], size=5), name=labelTWIST)

        Traces.append(TraceiDMM)
        Traces.append(TraceiTWIST)

    layout = go.Layout(scene=dict(xaxis_title='VLow (V)', yaxis_title='ILow (A)', zaxis_title='Efficiency (%)'))

    # Create a Figure object with the data and layout   
    fig = go.Figure(data=Traces, layout=layout)
    
    minzTWIST = min(EffTWIST_per)
    maxzTWIST = max(EffTWIST_per)
    
    my_plots["title"].append(title)
    my_plots["fig"].append(fig)
    my_plots["zMin"].append(minzTWIST)
    my_plots["zMax"].append(maxzTWIST)

    return my_plots

###################################################################
#                           PlotErr3D                             #
###################################################################
def InteractivePlotErr3D(TestsPathList, LowLeg, ErrorType, my_plots):

    Traces=[]#Initialise traces list
    i=0
    z=40 #We assume we will never have more than this different dataset to plot

    #List of 40 dark colors
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
                title = "TWIST instruments efficiency estimation absolute error for leg1"
                VLowTWIST_V = data['TWIST VLow1 (mV)']/1000
                ILowTWIST_A = data['TWIST ILow1 (mA)']/1000
                Err_Per = data["Efficiency Absolute error leg 1 (%)"]
                minzTWIST = min(Err_Per)
                maxzTWIST = max(Err_Per)

            elif(LowLeg == 2):
                title = "TWIST instruments efficiency estimation absolute error for leg2"
                VLowTWIST_V = data['TWIST VLow2 (mV)']/1000
                ILowTWIST_A = data['TWIST ILow2 (mA)']/1000
                Err_Per = data["Efficiency Absolute error leg 2 (%)"]
                minzTWIST = min(Err_Per)
                maxzTWIST = max(Err_Per)

        elif (ErrorType == "Rel"):
            if(LowLeg == 1):
                title = "TWIST instruments efficiency estimation relative error for leg1"
                VLowTWIST_V = data['TWIST VLow1 (mV)']/1000
                ILowTWIST_A = data['TWIST ILow1 (mA)']/1000
                Err_Per = data["Efficiency Relative error leg 1 (%)"]
                minzTWIST = -20
                maxzTWIST = 20

            elif(LowLeg == 2):
                title = "TWIST instruments efficiency estimation relative error for leg2"
                VLowTWIST_V = data['TWIST VLow2 (mV)']/1000
                ILowTWIST_A = data['TWIST ILow2 (mA)']/1000
                Err_Per = data["Efficiency Relative error leg 2 (%)"]
                minzTWIST = -20
                maxzTWIST = 20

        labelTWIST= lbl_volt_V 

        TraceiTWIST = go.Scatter3d(x=VLowTWIST_V, y=ILowTWIST_A, z=Err_Per, mode='markers', marker=dict(color=colors[z], size=5), name=labelTWIST)
        Traces.append(TraceiTWIST)
        
    if (ErrorType == "Abs"):
        zaxisTitle = "Absolute error of eff measure (%)"

    elif (ErrorType == "Rel"):
        zaxisTitle = "Relative error of eff measure (ratio)"

    layout = go.Layout(scene=dict(xaxis_title='VLow (V)', yaxis_title='ILow (A)', zaxis_title=zaxisTitle),
                title='3D Scatter Plot')

    # Create a Figure object with the data and layout
    fig = go.Figure(data=Traces, layout=layout)

    my_plots["title"].append(title)
    my_plots["fig"].append(fig)
    my_plots["zMin"].append(minzTWIST)
    my_plots["zMax"].append(maxzTWIST)

###################################################################
#                InteractivePlotPowerHighAbsError                 #
###################################################################
def InteractivePlotPowerHighAbsError(TestsPathList, my_plots):

    Traces=[]#Initialise traces list

    for TestPath in TestsPathList:
        
        #Getting test voltage for legend label
        TestNameNoCSV = os.path.basename(TestPath).replace('.csv', '')
        volt_match = re.findall(r'\d+V', TestNameNoCSV)
        lbl_volt_V = volt_match[0] if volt_match else ''

        data = pd.read_csv(TestPath, decimal=".", sep='\t')

        PowerHighDMM_W = data["DMM POWER High (W)"]
        Abs_Err_PowerHigh_W = data["Power High Absolute error (W)"] 

        Trace = go.Scatter(
            x=PowerHighDMM_W,
            y=Abs_Err_PowerHigh_W,
            name=lbl_volt_V,
            mode='markers')

        Traces.append(Trace)

        xaxis_lbl = 'DMM POWER High (W)'
        yaxis_lbl = 'Power High Absolute error (W)'
        title_lbl = 'Power High relative error (W) vs DMM POWER High (W)'

    layout = go.Layout(scene=dict(xaxis_title=xaxis_lbl, yaxis_title=yaxis_lbl),
            title=title_lbl)

    fig = go.Figure(data=Traces, layout=layout)

    title="TWIST instruments Power High absolute estimation error"

    my_plots["title"].append(title)
    my_plots["fig"].append(fig)
    my_plots["zMin"].append(min(Abs_Err_PowerHigh_W))
    my_plots["zMax"].append(max(Abs_Err_PowerHigh_W))

###################################################################
#                InteractivePlotPowerHighRelError                 #
###################################################################
def InteractivePlotPowerHighRelError(TestsPathList, my_plots):

    Traces=[]#Initialise traces list
    fig = plt.figure()

    for TestPath in TestsPathList:
        
        #Getting test voltage for legend label
        TestNameNoCSV = os.path.basename(TestPath).replace('.csv', '')
        volt_match = re.findall(r'\d+V', TestNameNoCSV)
        lbl_volt_V = volt_match[0] if volt_match else ''

        data = pd.read_csv(TestPath, decimal=".", sep='\t')

        PowerHighDMM_W = data["DMM POWER High (W)"]
        Rel_Err_PowerHigh_Per = data["Power High relative error (%)"] 

        Trace = go.Scatter(
            x=PowerHighDMM_W,
            y=Rel_Err_PowerHigh_Per,
            name=lbl_volt_V,
            mode='markers')

        Traces.append(Trace)

        xaxis_lbl = 'High side power DMM (W)'
        yaxis_lbl = 'Relative error on high side power measure (%)'
        title_lbl = 'Power High relative error (%) vs DMM POWER High (W)'

    layout = go.Layout(scene=dict(xaxis_title=xaxis_lbl, yaxis_title=yaxis_lbl),
            title=title_lbl)

    fig = go.Figure(data=Traces, layout=layout)

    miny = min(Rel_Err_PowerHigh_Per)
    maxy = max(Rel_Err_PowerHigh_Per)


    title="TWIST instruments Power High relative estimation error"

    my_plots["title"].append(title)
    my_plots["fig"].append(fig)
    my_plots["zMin"].append(miny)
    my_plots["zMax"].append(maxy)

###################################################################
#                InteractivePlotPowerLowAbsError                  #
###################################################################
def InteractivePlotPowerLowAbsError(TestsPathList, LowLeg, my_plots):

    Traces=[]#Initialise traces list
    fig = plt.figure()

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

        Trace = go.Scatter(
            x=DMMPowerLow_W,
            y=Abs_Err_PowerLow_Per,
            name=lbl_volt_V,
            mode='markers')

        Traces.append(Trace)

        xaxis_lbl = 'Low side power DMM (W)'
        yaxis_lbl = "Absolute error on low side " + " " + str(LowLeg) +  "power measure (W)"
        title_lbl = 'Power Low absolute error (W) vs DMM POWER Low (W)'

    layout = go.Layout(scene=dict(xaxis_title=xaxis_lbl, yaxis_title=yaxis_lbl),
            title=title_lbl)

    fig = go.Figure(data=Traces, layout=layout)

    miny = min(Abs_Err_PowerLow_Per)
    maxy = max(Abs_Err_PowerLow_Per)

    title = "TWIST instruments low side power estimation absolute error"
    my_plots["title"].append(title)
    my_plots["fig"].append(fig)
    my_plots["zMin"].append(miny)
    my_plots["zMax"].append(maxy)


###################################################################
#                InteractivePlotPowerLowRelError                  #
###################################################################
def InteractivePlotPowerLowRelError(TestsPathList, LowLeg, my_plots):

    Traces=[]#Initialise traces list
    fig = plt.figure()

    for TestPath in TestsPathList:
        
        #Getting test voltage for legend label
        TestNameNoCSV = os.path.basename(TestPath).replace('.csv', '')
        volt_match = re.findall(r'\d+V', TestNameNoCSV)
        lbl_volt_V = volt_match[0] if volt_match else ''

        data = pd.read_csv(TestPath, decimal=".", sep='\t')

        DMMPowerLow_W = data["DMM POWER Low (W)"]

        if(LowLeg == 1):
            Rel_Err_PowerLow_Per = data["Power Low1 relative error (%)"]

        elif(LowLeg == 2):
            Rel_Err_PowerLow_Per = data["Power Low2 relative error (%)"]

        Trace = go.Scatter(
            x=DMMPowerLow_W,
            y=Rel_Err_PowerLow_Per,
            name=lbl_volt_V,
            mode='markers')

        Traces.append(Trace)

        xaxis_lbl = 'Low side power DMM (W)'
        yaxis_lbl = "Relative error on low side " + str(LowLeg) +  " power measure (%)"
        title_lbl = 'Power Low relative error (%) vs DMM POWER Low (W)'

    layout = go.Layout(scene=dict(xaxis_title=xaxis_lbl, yaxis_title=yaxis_lbl),
            title=title_lbl)

    fig = go.Figure(data=Traces, layout=layout)

    miny = min(Rel_Err_PowerLow_Per)
    maxy = max(Rel_Err_PowerLow_Per)

    title = "TWIST instruments low side power estimation relative error"
    my_plots["title"].append(title)
    my_plots["fig"].append(fig)
    my_plots["zMin"].append(miny)
    my_plots["zMax"].append(maxy)
