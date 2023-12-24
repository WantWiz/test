"""
This page deploys an analysis of data acquired using the OwnBench test bench developped
developped by the OwnTech team. 
"""

#####################################################################################
#                             Imports / Initializations                             #
#####################################################################################
import os, csv, serial, pyvisa, time, sys, dash, math, re
from dash import dcc, html, Input, Output, callback, ALL
import dash_bootstrap_components as dbc
import matplotlib.pyplot as plt
import matplotlib, json
import base64, Coefficients
import pandas as pd
import webbrowser
from pages import setup_page
import numpy as np
from PIL import Image
import io, shutil

from fpdf import FPDF

ScriptPath = os.path.dirname('..')
LibFolderName = "Libraries"

LibPath = os.path.join(ScriptPath, LibFolderName)
# caution: path[0] is reserved for script path (or '' in REPL)
# sys.path.insert(0, LibPath)
sys.path.insert(1, LibPath)

import Settings, EAPSI9750, K2000, bk8500, Plot, ActiveLoad
import FileMngt, SPIN_Comm, OrganizeDataInCSV, InteractivePlot
import warnings, Accuracy, json
warnings.simplefilter("ignore", UserWarning)

# initialization of NumberOfEfficiencyGraphs, NumberOf3dEfficiencyGraphs, TestIndex and my_plots
if ("TestIndex" not in locals() and "NumberOfEfficiencyGraphs" not in locals() and "NumberOf3dEfficiencyGraphs" not in locals() 
    and "my_plots_histo" not in locals() and "my_plots_eff" not in locals() and "my_plots_coeffs_history" not in locals()
    and "my_plots_histo_history" not in locals()):
    NumberOfEfficiencyGraphs = 7
    NumberOf3dEfficiencyGraphs = 3
    TestIndex = 0
    my_plots_histo = {
        "title": [],
        "fig": [],
        "zMin": [],
        "zMax": [],
        "plot_IDs": [],
        "slider_IDs": [],
        "min_input_IDs": [],
        "max_input_IDs": []
    }
    my_plots_eff = {
        "title": [],
        "fig": [],
        "zMin": [],
        "zMax": [],
        "plot_IDs": [],
        "slider_IDs": [],
        "min_input_IDs": [],
        "max_input_IDs": []
    }
    my_plots_coeffs_history = {
        "title": [],
        "fig": [],
        "zMin": [],
        "zMax": [],
        "plot_IDs": [],
        "slider_IDs": [],
        "min_input_IDs": [],
        "max_input_IDs": []
    }
    my_plots_histo_history = {
        "title": [],
        "fig": [],
        "zMin": [],
        "zMax": [],
        "plot_IDs": [],
        "slider_IDs": [],
        "min_input_IDs": [],
        "max_input_IDs": []
    }

# creation of the variable that command the active button for test histo results
histo_results_active_button_index=0

# initialysation of my_plots_coeffs_history, my_plots_eff, my_plots_histo, my_plots_histo_history
def initialyseplots():
    global my_plots_coeffs_history, my_plots_eff, my_plots_histo, my_plots_histo_history
    my_plots_histo = {
        "title": [],
        "fig": [],
        "zMin": [],
        "zMax": [],
        "plot_IDs": [],
        "slider_IDs": [],
        "min_input_IDs": [],
        "max_input_IDs": []
    }
    my_plots_eff = {
        "title": [],
        "fig": [],
        "zMin": [],
        "zMax": [],
        "plot_IDs": [],
        "slider_IDs": [],
        "min_input_IDs": [],
        "max_input_IDs": []
    }
    my_plots_coeffs_history = {
        "title": [],
        "fig": [],
        "zMin": [],
        "zMax": [],
        "plot_IDs": [],
        "slider_IDs": [],
        "min_input_IDs": [],
        "max_input_IDs": []
    }
    my_plots_histo_history = {
        "title": [],
        "fig": [],
        "zMin": [],
        "zMax": [],
        "plot_IDs": [],
        "slider_IDs": [],
        "min_input_IDs": [],
        "max_input_IDs": []
    }



#####################################################################################
#                                 Coefficients Test                                 #
#####################################################################################

# function that create the layout for coeffs results
def DisplayLayoutCoeffs():

    # path of the csv that contains the calibration coefficients
    Dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(Dir)
    OutputCoeffsFolder = os.path.join(parent_dir, "Results")
    TestFolder = FileMngt.CreateSubfolder(OutputCoeffsFolder, Settings.JsonTestsHistory_data["TestNamesHistory"][TestIndex])
    TestFolder = FileMngt.CreateSubfolder(TestFolder, "Output_Coefficients")
    Path = TestFolder + '/' + 'Coeffs' + '_' + Settings.JsonTestsHistory_data["TestNamesHistory"][TestIndex] + '.csv'
    # transformation from csv to dataframe
    df = pd.read_csv(Path, delimiter="\t", encoding='latin-1') 
    df_list = df.values.tolist()

    # plot of test coeffs data (the same function is used to display test histo data)
    PlotTestsHistoCoeffsHistory("Coeffs_Results_History", "Coeffs", my_plots_coeffs_history)

    # Creation of two lists to store values of averages and standard deviations
    mean_list = []
    standard_deviation_list = []

    # distance from mean value
    DistanceFromMeanValue=[]

    # Browse dictionary keys and add values to appropriate lists
    for key, value in Settings.CoeffsHistoryMeanStandardDeviationDict.items():
        mean_list.append(value["Mean"])
        standard_deviation_list.append(value["StandartDeviation"])

    # adaptation of the display according to the BoardSN
    if Settings.JsonTestsHistory_data["LowLegHistory"][TestIndex] == 2:

        # we modify mean_list & standard_deviation_list to match with df_list[0] len
        index_to_remove_mean_standart_deviation = [0, 0, 4, 4]
        for index in index_to_remove_mean_standart_deviation:
            del mean_list[index]
            del standard_deviation_list[index]
        mean_list=[0, mean_list[0], mean_list[1], 0, mean_list[2], mean_list[3], 0, mean_list[4], mean_list[5], 0, mean_list[6], mean_list[7]]
        standard_deviation_list=[0, standard_deviation_list[0], standard_deviation_list[1], 0, standard_deviation_list[2], standard_deviation_list[3], 0, standard_deviation_list[4], standard_deviation_list[5], 0, standard_deviation_list[6], standard_deviation_list[7]]        

        # remove the coeffs which concern only BoardSN 1
        index_to_remove = [1, 1, 1, 7, 7, 7]
        for index in index_to_remove:
            del df_list[0][index]
        
        col = ["Board SN", "Voltage Gain side 2", "Voltage Offset side 2", "Correlation Coefficient", "Voltage Gain Entry", "Voltage Offset Entry", "Correlation Coefficient", "Current Gain side 2", "Current Offset side 2", "Correlation Coefficient", "Current Gain Entry", "Current Offset Entry", "Correlation Coefficient"]
        table_rows = []
        for i in range(len(col)):
            if i not in [0,3,6,9,12]:
                DistanceFromMeanValue.append(str(round(abs(df_list[0][i]-mean_list[i])/standard_deviation_list[i], 2)) + " σ")
                if (df_list[0][i] < mean_list[i]-2*standard_deviation_list[i] and df_list[0][i] >  mean_list[i]+2*standard_deviation_list[i]):
                    color="red"
                else:
                    color="green"
            else:
                DistanceFromMeanValue.append("")
                color = "grey"

            table_row = html.Tr([
                html.Td(col[i], style={'fontWeight': 'bold'}),
                html.Td(df_list[0][i], style={'color': color}),
                html.Td(DistanceFromMeanValue[i], style={'color': color})
            ])
            table_rows.append(table_row)

        table_coeffs = dbc.Table(
            table_rows,
            bordered=True,
            striped=True,
            responsive=True,
            hover=True
        )
        return html.H3("Calibration coefficients"), table_coeffs, DisplayLayoutTestsHistoCoeffsHistory(my_plots_coeffs_history["title"][0], my_plots_coeffs_history["fig"][0], my_plots_coeffs_history["zMin"][0], my_plots_coeffs_history["zMax"][0]), DisplayTableOfMeanAndStandartDeviationValues(Settings.CoeffsHistoryMeanStandardDeviationDict)
    
    elif Settings.JsonTestsHistory_data["LowLegHistory"][TestIndex] == 1:

        # we modify mean_list & standard_deviation_list to match with df_list[0] len
        index_to_remove_mean_standart_deviation = [2, 2, 6, 6]
        for index in index_to_remove_mean_standart_deviation:
            del mean_list[index]
            del standard_deviation_list[index]
        mean_list=[0, mean_list[0], mean_list[1], 0, mean_list[2], mean_list[3], 0, mean_list[4], mean_list[5], 0, mean_list[6], mean_list[7]]
        standard_deviation_list=[0, standard_deviation_list[0], standard_deviation_list[1], 0, standard_deviation_list[2], standard_deviation_list[3], 0, standard_deviation_list[4], standard_deviation_list[5], 0, standard_deviation_list[6], standard_deviation_list[7]]        

        # remove the coeffs which concern only BoardSN 2
        index_to_remove = [4, 4, 4, 10, 10, 10]
        for index in index_to_remove:
            del df_list[0][index]
        col = ["Board SN", "Voltage Gain side 1", "Voltage Offset side 1", "Correlation Coefficient", "Voltage Gain Entry", "Voltage Offset Entry", "Correlation Coefficient", "Current Gain side 1", "Current Offset side 1", "Correlation Coefficient", "Current Gain Entry", "Current Offset Entry", "Correlation Coefficient"]
        table_rows = []

        for i in range(len(col)):
            if i not in [0,3,6,9,12]:
                DistanceFromMeanValue.append(str(round(abs(df_list[0][i]-mean_list[i])/standard_deviation_list[i], 2)) + " σ")
                if (df_list[0][i] < mean_list[i]-2*standard_deviation_list[i] and df_list[0][i] >  mean_list[i]+2*standard_deviation_list[i]):
                    color="red"
                    
                else:
                    color="green"
            else:
                DistanceFromMeanValue.append("")
                color = "grey"
            
            table_row = html.Tr([
                html.Td(col[i], style={'fontWeight': 'bold'}),
                html.Td(df_list[0][i], style={'color': color}),
                html.Td(DistanceFromMeanValue[i], style={'color': color})
            ])
            table_rows.append(table_row)

        table_coeffs = dbc.Table(
            table_rows,
            bordered=True,
            striped=True,
            responsive=True,
            hover=True
        )
        return html.H3("Calibration coefficients"), table_coeffs, DisplayLayoutTestsHistoCoeffsHistory(my_plots_coeffs_history["title"][0], my_plots_coeffs_history["fig"][0], my_plots_coeffs_history["zMin"][0], my_plots_coeffs_history["zMax"][0]), DisplayTableOfMeanAndStandartDeviationValues(Settings.CoeffsHistoryMeanStandardDeviationDict)

# function that create the page of the pdf that presents the coeffs results
def PDFCoefficientsTest(pdf, SpaceBeetweenTestInfo, SpaceBeforeAfterTitle, TitleSize, DataAndSubtitlesSize):

    # add a new page
    pdf.add_page()

    # set the font style and size for the subtitle
    pdf.set_font("Arial", "B", DataAndSubtitlesSize)

    # add the subtitle
    pdf.cell(0, 10, "Converter Calibration Coefficients", ln=True)

    # add a new line for spacing
    pdf.ln(SpaceBeforeAfterTitle)

    # set the font style and size for the table
    pdf.set_font("Arial", "", DataAndSubtitlesSize)

    # path oh the csv that contains the calibration coeffs
    DirCoeffs = os.path.dirname(os.path.abspath(__file__))
    parent_dirCoeffs = os.path.dirname(DirCoeffs)
    OutputCoeffsFolder = os.path.join(parent_dirCoeffs, "Results")
    TestFolderCoeffs = FileMngt.CreateSubfolder(OutputCoeffsFolder, Settings.JsonTestsHistory_data["TestNamesHistory"][TestIndex])
    TestFolderCoeffs = FileMngt.CreateSubfolder(TestFolderCoeffs, "Output_Coefficients")

    PathCoeffs = TestFolderCoeffs + '/' + 'Coeffs' + '_' + Settings.JsonTestsHistory_data["TestNamesHistory"][TestIndex] + '.csv'

    # transformation from csv to dataframe
    df = pd.read_csv(PathCoeffs, delimiter="\t")
    df_list = df.values.tolist()

    # define the table data
    data = []

    for _ in range(13):
        data.append(["", ""])
    
    # we adapt the table to the leg
    if Settings.JsonTestsHistory_data["LowLegHistory"][TestIndex] == 1:

        row = ["Board SN", "Voltage Gain side 1", "Voltage Offset side 1", "Correlation Coefficient", "Voltage Gain Entry", "Voltage Offset Entry", "Correlation Coefficient", "Current Gain side 1", "Current Offset side 1", "Correlation Coefficient", "Current Gain Entry", "Current Offset Entry", "Correlation Coefficient"]

        for i in range(len(data)):
            data[i][0] = row[i]
        
        # we remove the columns that concern leg 2
        index_to_remove = [4, 4, 4, 10, 10, 10]
        for index in index_to_remove:
            del df_list[0][index]
        for i in range(len(df_list[0])):
            data[i][1] = df_list[0][i]

    if Settings.JsonTestsHistory_data["LowLegHistory"][TestIndex] == 2:

        row = ["Board SN", "Voltage Gain side 2", "Voltage Offset side 2", "Correlation Coefficient", "Voltage Gain Entry", "Voltage Offset Entry", "Correlation Coefficient", "Current Gain side 2", "Current Offset side 2", "Correlation Coefficient", "Current Gain Entry", "Current Offset Entry", "Correlation Coefficient"]

        for i in range(len(data)):
            data[i][0] = row[i]
        # we remove the columns that concern leg 1
        index_to_remove = [1, 1, 1, 7, 7, 7]
        for index in index_to_remove:
            del df_list[0][index]
        for i in range(len(df_list[0])):
            data[i][1] = df_list[0][i]

    # set the column widths
    col_width = pdf.w / 3

    # calculate the x-coordinate to center the table horizontally
    table_x = (pdf.w - 2*col_width) / 2

    # set the row height
    row_height = pdf.font_size * 1.5

    # add the table data
    for i, row in enumerate(data):
        pdf.set_x(table_x)
        pdf.set_font("Arial", "B", DataAndSubtitlesSize)
        pdf.cell(col_width, row_height, str(row[0]), border=1)
        pdf.set_font("Arial", "", DataAndSubtitlesSize)
        pdf.cell(col_width, row_height, str(row[1]), border=1)
        pdf.ln(row_height)

# callback that show/hide the coefficients results
@callback(
    Output("coefficients_results", "children"),
    Output("results-coefficients-collapse", "is_open"),
    Input("results_coefficients_button", "n_clicks"),
    [dash.dependencies.State("results-coefficients-collapse", "is_open"),
    dash.dependencies.State("TestNameAnalysis", "valid")]                
)
def coefficients_results_collapse(n, is_open, TestNameAnalysis_validity):
    if n and TestNameAnalysis_validity and "TestCoefficients" in Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]:
        initialyseplots()
        return DisplayLayoutCoeffs(), not is_open
    return None, is_open



#####################################################################################
#                                  Efficiency Test                                  #
#####################################################################################

# function that create the layout for the efficiency results
def createPlotLayoutEff(title: str, fig: list, zMin: list, zMax: list):
    marksCount = 5
    rows = []
    for i, f in enumerate(fig):
        plot_id = "my_plot_" + str(i)
        axis_id = "axis_slider_" + str(i)
        min_id = "min_input_id_" + str(i)
        max_id = "max_input_id_" + str(i)

        my_plots_eff["plot_IDs"].append(plot_id)
        my_plots_eff["slider_IDs"].append(axis_id)
        my_plots_eff["min_input_IDs"].append(min_id)
        my_plots_eff["max_input_IDs"].append(max_id)

        step = (zMax[i] - zMin[i]) / marksCount
        if step != 0:
            marks = {i: str(i) for i in range(math.floor(zMin[i]), math.ceil(zMax[i]), math.ceil(step))}
        else:
            marks = {}

        # only the 3d graphs must have a slider 
        if i <=(NumberOf3dEfficiencyGraphs-1):
            rows.append(
                dbc.Row(
                    [
                        html.H3(title[i], className="mt-4"),
                        dbc.Col(
                            html.Div(
                                [
                                    html.Label('Axis Range', 
                                            className="mt-5 mb-3 offset-md-4",
                                            ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Div(
                                                    [
                                                        dcc.RangeSlider(
                                                            id=axis_id,
                                                            min=math.floor(zMin[i]),
                                                            max=math.ceil(zMax[i]),
                                                            step=1,
                                                            value=[0, 100],
                                                            tooltip={"placement": "left", "always_visible": True},
                                                            vertical=True,
                                                            className="ms-3",
                                                            marks=marks
                                                        ),
                                                    ]
                                                ),
                                                width=6,
                                                className="offset-md-3",
                                            )
                                        ]
                                    ),
                                ]
                            ),
                            width=4,
                            className="mt-2"
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    dcc.Graph(
                                        id=plot_id,
                                        figure=fig[i],
                                        style={"height": "70vh"}
                                    ),
                                ],
                            ),
                            width=8,
                            className="mt-2",
                        ),
                    ]
                )
            )
        else:
            # no slider
            rows.append(
                dbc.Row(
                    [
                        html.H3(title[i], className="mt-4"),

                        dbc.Col(
                            html.Div(
                                [
                                    dcc.Graph(
                                        id=plot_id,
                                        figure=fig[i],
                                        style={"height": "70vh"}
                                    ),
                                ],
                            ),
                            width=15,
                            className="mt-2",
                        ),
                    ]
                )
            )

    # Set app layout
    return dbc.Container(rows)

# function that create the page of the pdf that presents the efficiency results
def PDFEfficiencyTest(pdf, SpaceBeetweenTestInfo, SpaceBeforeAfterTitle, TitleSize, DataAndSubtitlesSize):

    # add newpage
    pdf.add_page()

    # set the font style and size for the subtitle
    pdf.set_font("Arial", "B", DataAndSubtitlesSize)

    # add the subtitle
    pdf.cell(0, 10, "Converter Efficiency", ln=True)

    # add a new line for spacing
    pdf.ln(SpaceBeforeAfterTitle)

    # path of the image that contains the 2d efficiency graphs
    FolderNameEff = Settings.JsonTestsHistory_data["TestNamesHistory"][TestIndex]
    output_file_folderEff = "Results/" + FolderNameEff + "/Output_Efficiency"
    FolderEff = os.path.join(ScriptPath, output_file_folderEff)

    TestNameEff = Settings.JsonTestsHistory_data["TestNamesHistory"][TestIndex] + "_Eff2D.png"
    PathEff = os.path.join(FolderEff, TestNameEff)

    img_width_eff = pdf.w   # Adjust the width as desired
    img_height_eff = 0  # Set to 0 to maintain aspect ratio

    # Calculate the x-coordinate to center the image horizontally
    x_eff = (pdf.w - img_width_eff) / 2

    # Add the image
    pdf.image(PathEff, x=x_eff, y=pdf.get_y(), w=img_width_eff, h=img_height_eff, type='', link='')

# function that create the graphs from the results associated with the test chosen by the user
def plot_interactive_graphs(TestIndex):
    FolderName = Settings.JsonTestsHistory_data["TestNamesHistory"][TestIndex]
    output_file_folder = "Results/" + FolderName + "/Output_Efficiency"
    Folder = os.path.join(ScriptPath, output_file_folder)

    TestNames = []
    for v in Settings.JsonTestsHistory_data["EffVHighStepArray_V_History"][TestIndex]:
        TestNames.append(FolderName + "_" + str(v) + "V_AVGD.csv")
    PathLists = []

    for name in TestNames:
        PathLists.append(os.path.join(Folder, name))

    for path in PathLists:
        OrganizeDataInCSV.ComputeTWISTPowerErr(path)
    InteractivePlot.InteractivePlotEff3D(PathLists, Settings.JsonTestsHistory_data["LowLegHistory"][TestIndex], my_plots_eff)
    InteractivePlot.InteractivePlotErr3D(PathLists, Settings.JsonTestsHistory_data["LowLegHistory"][TestIndex], "Abs", my_plots_eff)
    InteractivePlot.InteractivePlotErr3D(PathLists, Settings.JsonTestsHistory_data["LowLegHistory"][TestIndex], "Rel", my_plots_eff)

    InteractivePlot.InteractivePlotPowerHighAbsError(PathLists, my_plots_eff)
    InteractivePlot.InteractivePlotPowerHighRelError(PathLists, my_plots_eff)
    InteractivePlot.InteractivePlotPowerLowAbsError(PathLists, Settings.JsonTestsHistory_data["LowLegHistory"][TestIndex], my_plots_eff)
    InteractivePlot.InteractivePlotPowerLowRelError(PathLists, Settings.JsonTestsHistory_data["LowLegHistory"][TestIndex], my_plots_eff)
        
    for i in range(NumberOfEfficiencyGraphs):
        plot_id = "my_plot_" + str(i)
        axis_id = "axis_slider_" + str(i)
        min_id = "min_input_id_" + str(i)
        max_id = "max_input_id_" + str(i)

        my_plots_eff["plot_IDs"].append(plot_id)
        my_plots_eff["slider_IDs"].append(axis_id)
        my_plots_eff["min_input_IDs"].append(min_id)
        my_plots_eff["max_input_IDs"].append(max_id)

# initialisation of my_plot before the user choose the test results he wants to display
plot_interactive_graphs(1)

# callback that show/hide the efficiency results
@callback(
    Output("efficiency_results", "children"),
    Output("results-efficiency-collapse", "is_open"),
    Input("results_efficiency_button", "n_clicks"),           
    [dash.dependencies.State("results-efficiency-collapse", "is_open"),
    dash.dependencies.State("TestNameAnalysis", "valid")]                  
)
def efficiency_results_collapse(n, is_open, TestNameAnalysis_validity):
    if n and TestNameAnalysis_validity and "TestEfficiency" in Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]:
        initialyseplots()
        plot_interactive_graphs(TestIndex)
        return createPlotLayoutEff(my_plots_eff["title"], my_plots_eff["fig"], my_plots_eff["zMin"], my_plots_eff["zMax"]), not is_open
    return None, is_open

# callback that update the Z-axis range from the slider's values
for i in range(NumberOf3dEfficiencyGraphs):
    @callback(
        dash.dependencies.Output(my_plots_eff["plot_IDs"][i], 'figure'),
        [dash.dependencies.Input(my_plots_eff["slider_IDs"][i], 'value')]
    )
    def update_zaxis_range(axis_range, j=i):
        if(my_plots_eff["fig"][j].data[0].type == "scatter3d"):
            my_plots_eff["fig"][j].update_layout(
                scene=dict(
                    zaxis=dict( 
                        range=axis_range
                    )
                )
            )
            return my_plots_eff["fig"][j]
    @callback(
        dash.dependencies.Output(my_plots_eff["slider_IDs"][i], 'value'),
        [dash.dependencies.Input(my_plots_eff["min_input_IDs"][i], 'value'), 
         dash.dependencies.Input(my_plots_eff["max_input_IDs"][i], 'value')]
    )
    def update_zaxis_range(tooltip_value_min, tooltip_value_max):
        return [tooltip_value_min, tooltip_value_max]



#####################################################################################
#                                   Accuracy Test                                   #
#####################################################################################

# function that create the layout for the accuracy results
def DisplayPlotLayoutAcc():
    
    # path of the images
    FolderName = Settings.JsonTestsHistory_data["TestNamesHistory"][TestIndex]
    output_file_folder = "Results/" + FolderName + "/Output_Accuracy"
    Folder = os.path.join(ScriptPath, output_file_folder)
    TestName1 = FolderName + "_All_Abs.png"
    TestName2 = FolderName + "_All_Rel.png"

    Path1 = os.path.join(Folder, TestName1)
    Path2 = os.path.join(Folder, TestName2)
    
    # opening images
    with open(Path1, "rb") as file:
        img_data1 = file.read()
    with open(Path2, "rb") as file:
        img_data2 = file.read()

    # decoding images
    img_base64_1 = base64.b64encode(img_data1).decode("utf-8")
    img_base64_2 = base64.b64encode(img_data2).decode("utf-8")

    # displays images and titles
    img1 = html.Img(src="data:image/png;base64," + img_base64_1, alt="Image")
    img2 = html.Img(src="data:image/png;base64," + img_base64_2, alt="Image")
    img1_div = html.Div(img1, className="text-center")
    img2_div = html.Div(img2, className="text-center")

    title1 = html.H3("Measures absolute error (mV)")
    title2 = html.H3("Measures relative error (%)")
    return title1, img1_div, html.Hr(), title2, img2_div

# function that create the page of the pdf that presents the accuracy results
def PDFAccuracyTest(pdf, SpaceBeetweenTestInfo, SpaceBeforeAfterTitle, TitleSize, DataAndSubtitlesSize):

    # add newpage
    pdf.add_page()

    # set the font style and size for the subtitle
    pdf.set_font("Arial", "B", DataAndSubtitlesSize)

    # add the subtitle
    pdf.cell(0, 10, "Converter Accuracy", ln=True)

    # add a new line for spacing
    pdf.ln(SpaceBeforeAfterTitle)
    
    # path of the image with the results of test accuracy
    FolderNameAcc = Settings.JsonTestsHistory_data["TestNamesHistory"][TestIndex]
    output_file_folderAcc = "Results/" + FolderNameAcc + "/Output_Accuracy"
    FolderAcc = os.path.join(ScriptPath, output_file_folderAcc)
    TestNameAcc = FolderNameAcc + "_All_Rel.png"

    PathAcc = os.path.join(FolderAcc, TestNameAcc)

    img_width_acc = pdf.w   # Adjust the width as desired
    img_height_acc = 0  # Set to 0 to maintain aspect ratio

    # calculate the x-coordinate to center the image horizontally
    x_acc = (pdf.w - img_width_acc) / 2

    # add the image
    pdf.image(PathAcc, x=x_acc, y=pdf.get_y(), w=img_width_acc, h=img_height_acc, type='', link='')

# callback that show/hide the accuracy results
@callback(
    Output("accuracy_results", "children"),
    Output("results-accuracy-collapse", "is_open"),
    Input("results_accuracy_button", "n_clicks"),           
    dash.dependencies.State("results-accuracy-collapse", "is_open"), 
    dash.dependencies.State("TestNameAnalysis", "valid")                 
)
def accuracy_results_collapse(n, is_open, TestNameAnalysis_validity):
    if n and TestNameAnalysis_validity and "TestAccuracy" in Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]:
        return DisplayPlotLayoutAcc(), not is_open
    return None, is_open



#####################################################################################
#                                  Histogram Test                                   #
#####################################################################################

def PlotHistogram():
    # path of the results of the test 
    Dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(Dir)
    OutputHistogramFolder = os.path.join(parent_dir, "Results")
    TestFolder = FileMngt.CreateSubfolder(OutputHistogramFolder, Settings.JsonTestsHistory_data["TestNamesHistory"][TestIndex])
    TestFolder = FileMngt.CreateSubfolder(TestFolder, "Output_Histogram")
    Path = TestFolder + '/' + Settings.JsonTestsHistory_data["TestNamesHistory"][TestIndex] + "_" + str(Settings.JsonTestsHistory_data["HistVHighStepArray_mV_history"][TestIndex][histo_results_active_button_index]) + ".csv"
    Plot.PlotHistoDistrib(Path, "noShow", 4, my_plots_histo)
    HistoHistoryCSVName="Histo_Test_History_" + str(Settings.JsonTestsHistory_data["HistVHighStepArray_mV_history"][TestIndex][histo_results_active_button_index]) + "V"
    PlotTestsHistoCoeffsHistory("Histo_Test_History", HistoHistoryCSVName, my_plots_histo_history)


def PDFHistogramTest(pdf, SpaceBeetweenTestInfo, SpaceBeforeAfterTitle, TitleSize, DataAndSubtitlesSize):

    # add a new page
    pdf.add_page()

    # set the font style and size for the subtitle
    pdf.set_font("Arial", "B", DataAndSubtitlesSize)

    # add the subtitle
    pdf.cell(0, 10, "Histograms", ln=True)

    # path of the image with the results of test accuracy
    FolderNameHist = Settings.JsonTestsHistory_data["TestNamesHistory"][TestIndex]
    output_file_folderHist = "Results/" + FolderNameHist + "/Output_Histogram"
    FolderHist = os.path.join(ScriptPath, output_file_folderHist)
    TestNameHist = "Histograms_" + str(Settings.JsonTestsHistory_data["TestNamesHistory"][TestIndex]) + ".png"

    PathHist = os.path.join(FolderHist, TestNameHist)

    img_width_hist = pdf.w   # Adjust the width as desired
    img_height_hist = 0  # Set to 0 to maintain aspect ratio

    # calculate the x-coordinate to center the image horizontally
    x_hist = (pdf.w - img_width_hist) / 2

    # add the image
    pdf.image(PathHist, x=x_hist, y=pdf.get_y(), w=img_width_hist, h=img_height_hist, type='', link='')

    ### second part, display of the table with mean value and standart daviation for each measure
    
    # set the column widths
    col_width = pdf.w / 4
    # set the row height
    row_height = pdf.font_size * 1.5
    # calculate the xy-coordinate to place the table
    table_x = (pdf.w - 3*col_width) / 2
    table_y = pdf.h / 2 + 20
    pdf.set_xy(table_x, table_y)

    # add the subtitle
    pdf.cell(0, 10, "Histograms Means values and Standart Deviations", ln=True)

    # add a new line for spacing
    pdf.ln(10)

    data = [['Measure', 'Mean value', 'Standard Deviation']]
    for key, values in Settings.HistMeanStandardDeviationDict.items():
        variable = key
        mean = values['Mean']
        StandartDeviation = values['StandartDeviation']
        data.append([variable, mean, StandartDeviation])

    for i, row in enumerate(data):
        pdf.set_x(table_x)
        pdf.set_font("Arial", "B", DataAndSubtitlesSize)
        pdf.cell(col_width, row_height, str(row[0]), border=1)
        pdf.set_x(table_x + col_width)
        pdf.set_font("Arial", "", DataAndSubtitlesSize)
        pdf.cell(col_width, row_height, str(row[1]), border=1)
        pdf.set_x(table_x + 2*col_width)
        pdf.set_font("Arial", "", DataAndSubtitlesSize)
        pdf.cell(col_width, row_height, str(row[2]), border=1)
        pdf.ln(row_height)

def DisplayLayoutHist(title: str, fig: list, zMin: list, zMax: list):
    
    i=0
    plot_id = "my_plot_" + str(i)
    axis_id = "axis_slider_" + str(i)
    min_id = "min_input_id_" + str(i)
    max_id = "max_input_id_" + str(i)

    my_plots_histo["plot_IDs"].append(plot_id)
    my_plots_histo["slider_IDs"].append(axis_id)
    my_plots_histo["min_input_IDs"].append(min_id)
    my_plots_histo["max_input_IDs"].append(max_id)

    marksCount = 5
    rows = []

    plot_id = "my_plot_" + str(i)
    axis_id = "axis_slider_" + str(i)
    min_id = "min_input_id_" + str(i)
    max_id = "max_input_id_" + str(i)

    my_plots_histo["plot_IDs"].append(plot_id)
    my_plots_histo["slider_IDs"].append(axis_id)
    my_plots_histo["min_input_IDs"].append(min_id)
    my_plots_histo["max_input_IDs"].append(max_id)

    step = (zMax - zMin) / marksCount
    if step != 0:
        marks = {i: str(i) for i in range(math.floor(zMin), math.ceil(zMax), math.ceil(step))}
    else:
        marks = {}
    # no slider
    rows.append(
        dbc.Row(
            [
                html.H3(title, className="mt-4"),

                dbc.Col(
                    html.Div(
                        [
                            dcc.Graph(
                                id=plot_id,
                                figure=fig,
                                style={"height": "200vh"}
                            ),
                        ],
                    ),
                    width=15,
                    className="mt-2",
                ),
            ]
        )
    )
    # Set app layout
    return (dbc.Container(rows), DisplayTableOfMeanAndStandartDeviationValues(Settings.HistMeanStandardDeviationDict), 
            DisplayLayoutTestsHistoCoeffsHistory(my_plots_histo_history["title"][0], my_plots_histo_history["fig"][0], my_plots_histo_history["zMin"][0], my_plots_histo_history["zMax"][0]), 
            DisplayTableOfMeanAndStandartDeviationValues(Settings.HistoHistoryMeanStandardDeviationDictLeg1),
            DisplayLayoutTestsHistoCoeffsHistory(my_plots_histo_history["title"][1], my_plots_histo_history["fig"][1], my_plots_histo_history["zMin"][1], my_plots_histo_history["zMax"][1]), 
            DisplayTableOfMeanAndStandartDeviationValues(Settings.HistoHistoryMeanStandardDeviationDictLeg2))

@callback(
    Output("histogram_results", "children"),
    Output("results-histogram-collapse", "is_open"),
    Input("results_histogram_button", "n_clicks"),
    Input("HistNumberOfXAxisDivision", "valid"),
    Input("button_group_for_test_histo_voltage_choice", "n_clicks"),
    [dash.dependencies.State("results-histogram-collapse", "is_open"),
    dash.dependencies.State("TestNameAnalysis", "valid")]                
)
def histogram_results_collapse(n_results_histogram_button, HistNumberOfXAxisDivision_validity, n_button_group_for_test_histo_voltage_choice, is_open, TestNameAnalysis_validity):
    if TestNameAnalysis_validity and "TestHistogram" in Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex] and (n_results_histogram_button or HistNumberOfXAxisDivision_validity or n_button_group_for_test_histo_voltage_choice):
        initialyseplots()
        PlotHistogram()
        return DisplayLayoutHist(my_plots_histo["title"][0], my_plots_histo["fig"][0], my_plots_histo["zMin"][0], my_plots_histo["zMax"][0]), not is_open
    return None, is_open

# callback that check and update the value input by the user concerning the accuracy of the histogram
@callback(
    Output("HistNumberOfXAxisDivision", "valid"),
    Output("HistNumberOfXAxisDivision", "invalid"),
    [Input("HistNumberOfXAxisDivision", "n_submit"), Input("HistNumberOfXAxisDivision", "n_blur")],
    dash.dependencies.State("HistNumberOfXAxisDivision", "value")
)
def check_HistNumberOfXAxisDivision_validity(HistNumberOfXAxisDivision_n_submit, HistNumberOfXAxisDivision_n_blur, HistNumberOfXAxisDivision_value):
    if HistNumberOfXAxisDivision_value and (HistNumberOfXAxisDivision_n_submit or HistNumberOfXAxisDivision_n_blur):
        if str(HistNumberOfXAxisDivision_value).isdigit() and int(HistNumberOfXAxisDivision_value) >= 1 and int(HistNumberOfXAxisDivision_value) <= 10000:
            Plot.HistNumberOfXAxisDivision = int(HistNumberOfXAxisDivision_value)
            return True, False
        return False, True
    return False, False

# function that create a table that display the mean value and standart deviation for the TWIST's measures
def DisplayTableOfMeanAndStandartDeviationValues(MeanStandardDeviationDict):
    table_rows = [
        html.Tr([
            html.Td(html.Strong(key)),
            html.Td(value['Mean']),
            html.Td(value['StandartDeviation'])
        ])
        for key, value in MeanStandardDeviationDict.items()
    ]

    table = dbc.Table(
        children=[
            html.Thead(html.Tr([
                html.Th('Measure'),
                html.Th('Mean value'),
                html.Th('Standard Deviation')
            ]))
        ] + table_rows,
        bordered=True,
        striped=True,
        responsive=True
    )
    return table

def buttons_for_test_histo_voltage_choice():
    global histo_results_active_button_index
    histo_results_active_button_index = int(histo_results_active_button_index)
    return(
    dbc.ButtonGroup(
    [
        dbc.Button(
            str(Settings.JsonTestsHistory_data["HistVHighStepArray_mV_history"][TestIndex][i]) + " V",
            id={"type": "button", "index": i},
            outline=True,
            color="primary",
            active=i == histo_results_active_button_index,
        )
    for i in range(len(Settings.JsonTestsHistory_data["HistVHighStepArray_mV_history"][TestIndex])) if Settings.JsonTestsHistory_data["HistVHighStepArray_mV_history"][TestIndex] !=[]
    ],
    id="button_group_for_test_histo_voltage_choice",
    style={"display": "flex", "justify-content": "center"},
    )
    )

@callback(
    Output("button_group_for_test_histo_voltage_choice", "children"),
    Input({"type": "button", "index": ALL}, "n_clicks"),
    Input("TestNameAnalysis", "valid"),
    dash.dependencies.State({"type": "button", "index": ALL}, "id")
)
def update_button_group(n_clicks_list, button_ids, TestNameAnalysis_valid):
    ctx = dash.callback_context
    triggered_prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
    global histo_results_active_button_index
    if triggered_prop_id == "TestNameAnalysis" and TestNameAnalysis_valid:
        return buttons_for_test_histo_voltage_choice()
    else:
        triggered_prop_id = json.loads(triggered_prop_id)
        # Get the index of the button clicked from the ID
        global histo_results_active_button_index
        histo_results_active_button_index = triggered_prop_id["index"]
        # Update the 'active' attribute of the clicked button and deactivate the others
        return buttons_for_test_histo_voltage_choice()



#####################################################################################
#                                  Results Report                                   #
#####################################################################################

# creation of the results report card
ResultsReportCard = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Results Report", className="results_report", style={"text-align": "center"}),
                html.P("Click below to generate a results report", className="results_report_Card", style={"text-align": "center"}),
                dbc.Button("Generate Results Report", id="generate_results_button", color="warning", n_clicks=0, style={"display": "block", "margin": "auto"}),
            ]
        ),
    ],
    style={"width": "18rem", "margin": "auto", "marginTop": "0%"},
)

# function that create the pdf results report 
def PDFCreation():

    SpaceBeetweenTestInfo=3
    SpaceBeforeAfterTitle=10
    TitleSize=16
    DataAndSubtitlesSize=10

    # creation of a PDF object
    pdf = FPDF()

    # add newpage
    pdf.add_page()

    # set the font style and size for the title
    pdf.set_font("Arial", "B", TitleSize)

    # add the title
    pdf.cell(0, 10, "Tests Results for the TWIST 1.1.2", ln=True, align="C")

    # add a new line for spacing
    pdf.ln(SpaceBeforeAfterTitle)

    # set the font style and size for the test informations
    pdf.set_font("Arial", "", DataAndSubtitlesSize)

    # display of : TestName, LowLeg, BoardSN and the tests done
    pdf.cell(0, 8, "Test: " + Settings.JsonTestsHistory_data["TestNamesHistory"][TestIndex], ln=True)
    pdf.ln(SpaceBeetweenTestInfo)
    pdf.cell(0, 8, "Leg: " + str(Settings.JsonTestsHistory_data["LowLegHistory"][TestIndex]), ln=True) 
    pdf.ln(SpaceBeetweenTestInfo)
    pdf.cell(0, 8, "Board serial number: " + str(Settings.JsonTestsHistory_data["BoardSNHistory"][TestIndex]), ln=True) 
    pdf.ln(SpaceBeetweenTestInfo)
    pdf.cell(0, 8, "Converter type: " + str(Settings.JsonTestsHistory_data["ConverterTypeHistory"][TestIndex]), ln=True) 
    pdf.ln(SpaceBeetweenTestInfo)
    pdf.cell(0, 8, "Power supply type: " + str(Settings.JsonTestsHistory_data["PowerSupplyTypeHistory"][TestIndex]), ln=True) 
    pdf.ln(SpaceBeetweenTestInfo)
    pdf.cell(0, 8, "Load type: " + str(Settings.JsonTestsHistory_data["LoadTypeHistory"][TestIndex]), ln=True) 
    pdf.ln(SpaceBeetweenTestInfo)

    pdf.cell(0, 8, "Results for test: ", ln=True) 
    for test in Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]:
        pdf.cell(0, 8, test, ln=True)

    # add a new line for spacing
    pdf.ln(SpaceBeforeAfterTitle)

    # set the font style and size for the title
    pdf.set_font("Arial", "B", DataAndSubtitlesSize)

    # add the subtitle
    pdf.cell(0, 10, "Tests parameters", ln=True)  

    # add a new line for spacing
    pdf.ln(SpaceBeforeAfterTitle)

    # path of the json that contains the parameters of the test
    DirJson = os.path.dirname(os.path.abspath(__file__))
    DirJson = os.path.dirname(DirJson)
    DirJson = os.path.join(DirJson, "Results")
    TestFolderPathJson = os.path.join(DirJson, Settings.JsonTestsHistory_data["TestNamesHistory"][TestIndex])
    JsonPath = TestFolderPathJson + "\json_" + Settings.JsonTestsHistory_data["TestNamesHistory"][TestIndex] + ".json"
    with open(JsonPath, "r") as f:
        JsonTestData = json.load(f)

    DataTable = []
    for key, value in JsonTestData.items():
        if not isinstance(value, list):
            DataTable.append([key, value])

    # set the column widths
    col_width1 = pdf.w / 3
    col_width2 = pdf.w / 3

    # calculate the x-coordinate to center the table horizontally
    table_x = (pdf.w - (col_width1 + col_width2)) / 2

    # set the row height
    row_height = pdf.font_size * 1.5

    # add the table data
    for i, row in enumerate(DataTable):
        pdf.set_x(table_x)
        pdf.set_font("Arial", "B", DataAndSubtitlesSize)
        pdf.cell(col_width1, row_height, str(row[0]), border=1)
        pdf.set_font("Arial", "", DataAndSubtitlesSize)
        pdf.cell(col_width2, row_height, str(row[1]), border=1)
        pdf.ln(row_height)

    # display of the results of the tests done
    if "TestCoefficients" in Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]:
        PDFCoefficientsTest(pdf, SpaceBeetweenTestInfo, SpaceBeforeAfterTitle, TitleSize, DataAndSubtitlesSize)
    if "TestAccuracy" in Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]:
        PDFAccuracyTest(pdf, SpaceBeetweenTestInfo, SpaceBeforeAfterTitle, TitleSize, DataAndSubtitlesSize)
    if "TestEfficiency" in Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]:
        PDFEfficiencyTest(pdf, SpaceBeetweenTestInfo, SpaceBeforeAfterTitle, TitleSize, DataAndSubtitlesSize)
    if "TestHistogram" in Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]:
        PlotHistogram()
        PDFHistogramTest(pdf, SpaceBeetweenTestInfo, SpaceBeforeAfterTitle, TitleSize, DataAndSubtitlesSize)
    TestFolderPathPDF = TestFolderPathJson
    pdf_filename = os.path.join(TestFolderPathPDF, "TestsResults_" + Settings.JsonTestsHistory_data["TestNamesHistory"][TestIndex] + ".pdf")
    
    # save the PDF file
    pdf.output(pdf_filename)
    # automatic opening of the pdf in a new tab
    webbrowser.open(pdf_filename)

# callback that create the pdf with the results
@callback(
        Output("generate_results_button","children"),
        Input("generate_results_button", "n_clicks"),
        dash.dependencies.State("TestNameAnalysis", "valid")
)
def generate_report(n, TestNameAnalysis_validity):
    if n and TestNameAnalysis_validity:
        PDFCreation()
        return "PDF Created"
    return "Generate Results Report"



#####################################################################################
#                                    Test Results                                   #
#####################################################################################

# refresh TestNamesResultsOptions
def refresh_TestNamesResultsOptions():
    TestNamesResultsOptions = []

    for testname in Settings.JsonTestsHistory_data["TestNamesHistory"]:
        TestNamesResultsOptions.append({"label": testname, "value": testname})

    # delete DefaultParameters
    del TestNamesResultsOptions[0]
    return TestNamesResultsOptions

# callback that refresh TestNamesResultsOptions
@callback(
        Output("TestNameAnalysis", "options"),
        dash.dependencies.Input("results_displayable_collapse", "children")
)
def refresh_history(results_displayable_collapse):
    Settings.refresh_JsonTestsHistory()
    return refresh_TestNamesResultsOptions()

# creation of the input that allow the user to choose which test results he wants to display
def load_results_input():
    TestNamesResultsOptions = []

    for testname in Settings.JsonTestsHistory_data["TestNamesHistory"]:
        TestNamesResultsOptions.append({"label": testname, "value": testname})

    # delete DefaultParameters
    del TestNamesResultsOptions[0]
    return(
                dbc.InputGroup([
                    dbc.InputGroupText("Name of the test from which you want to load the results"),
                    dbc.Select(
                        id="TestNameAnalysis",
                        options=TestNamesResultsOptions,
                        value=None,
                        valid=False,
                        invalid=False,
                        persistence_type='memory', 
                        persistence=True
                    )
                ])
)

# callback that check and update TestNameAnalysis from the input of the user
@callback(
        Output("TestNameAnalysis", "valid"),
        Output("TestNameAnalysis", "invalid"),
        Input("TestNameAnalysis", "value")
)
def test_name_analysis_validity(value):
    if value is None:
        return False, False
    if value in Settings.JsonTestsHistory_data["TestNamesHistory"]:
        global TestIndex
        for i in range(len(Settings.JsonTestsHistory_data["TestNamesHistory"])):
            if value == Settings.JsonTestsHistory_data["TestNamesHistory"][i]:
                TestIndex = i
        return True, False 
    else:
        return False, True

# callback that display which test results can be display from the test chosen by the user
@callback(
        Output("results_displayable_collapse", "is_open"),
        Output("results_displayable_collapse", "children"),
        [dash.dependencies.Input("TestNameAnalysis", "valid")]
)
def results_displayable_collapse(TestNameAnalysis_validity):
    if TestNameAnalysis_validity:
        if len(Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]) == 4:
            return True, html.H6("You can display the results of the following test(s): " + Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex][0] + ", " + Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex][1] + ", " + Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex][2] + "and " + Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex][3])  
        elif len(Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]) == 3:
            return True, html.H6("You can display the results of the following test(s): " + Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex][0] + ", " + Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex][1] + " and " + Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex][2])                
        elif len(Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]) == 2:
            return True, html.H6("You can display the results of the following test(s): " + Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex][0] + " and " + Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex][1])
        elif len(Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]) == 1:
            return True, html.H6("You can display the results of the following test(s): " + Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex][0])
        else:
            return True, html.H6("No results displayable")
    return False, html.H6("")

# function that creates graphs of coefficients test data and histogram test data according to the arguments given to it
def PlotTestsHistoCoeffsHistory(FolderName, CSVName, my_plots):
	# path of the results of the test 
    Dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(Dir)
    OutputHistogramFolder = os.path.join(parent_dir, "Results")
    CoeffsTestHistoryFolder = os.path.join(OutputHistogramFolder, FolderName)
    Path = CoeffsTestHistoryFolder + "/" + CSVName + ".csv"
    if CSVName == "Coeffs":
        Plot.PlotHistoDistribCoeffsHistory(Path, "noShow", 4, my_plots)
    else:
        CoeffsTestHistoryFolder1 = os.path.join(CoeffsTestHistoryFolder, "LEG_1")
        Path1 = CoeffsTestHistoryFolder1 + "/" + CSVName + ".csv"
        CoeffsTestHistoryFolder2 = os.path.join(CoeffsTestHistoryFolder, "LEG_2")
        Path2 = CoeffsTestHistoryFolder2 + "/" + CSVName + ".csv"
        Plot.PlotHistoDistribHistoHistory(Path1, "noShow", 4, my_plots)
        Plot.PlotHistoDistribHistoHistory(Path2, "noShow", 4, my_plots)

# function that displays graphs of test data and histogram test data coefficients according to the arguments given to it
def DisplayLayoutTestsHistoCoeffsHistory(title: str, fig: list, zMin: list, zMax: list):

    i=0
    plot_id = "my_plot_" + str(i)
    axis_id = "axis_slider_" + str(i)
    min_id = "min_input_id_" + str(i)
    max_id = "max_input_id_" + str(i)

    my_plots_histo["plot_IDs"].append(plot_id)
    my_plots_histo["slider_IDs"].append(axis_id)
    my_plots_histo["min_input_IDs"].append(min_id)
    my_plots_histo["max_input_IDs"].append(max_id)

    marksCount = 5
    rows = []

    plot_id = "my_plot_" + str(i)
    axis_id = "axis_slider_" + str(i)
    min_id = "min_input_id_" + str(i)
    max_id = "max_input_id_" + str(i)

    my_plots_histo["plot_IDs"].append(plot_id)
    my_plots_histo["slider_IDs"].append(axis_id)
    my_plots_histo["min_input_IDs"].append(min_id)
    my_plots_histo["max_input_IDs"].append(max_id)

    step = (zMax - zMin) / marksCount
    if step != 0:
        marks = {i: str(i) for i in range(math.floor(zMin), math.ceil(zMax), math.ceil(step))}
    else:
        marks = {}
    # no slider
    rows.append(
        dbc.Row(
            [
                html.H3(title, className="mt-4"),

                dbc.Col(
                    html.Div(
                        [
                            dcc.Graph(
                                id=plot_id,
                                figure=fig,
                                style={"height": "200vh"}
                            ),
                        ],
                    ),
                    width=15,
                    className="mt-2",
                ),
            ]
        )
    )

    # Set app layout
    return dbc.Container(rows)#, DisplayTableOfMeanAndStandartDeviationValues(Settings.CoeffsHistoryMeanStandardDeviationDict)



#####################################################################################
#                                      LAYOUT                                       #
#####################################################################################

# display of the layout
layout = html.Div([
    html.H1("Analysis"),
    html.Hr(),
    load_results_input(),
    html.Div(style={"height": "15px"}), 
    dbc.Collapse([
        html.H6(""),
            ],
        id="results_displayable_collapse", 
        is_open=False,
    ),
    html.Hr(),
    html.Div(
        [
            dbc.Button(
                "Results Coefficients",
                id="results_coefficients_button",
                n_clicks=0,
                style={"width": "100%", "display": "block", "margin": "auto"},
            ),
            dbc.Collapse(
                [
                    dbc.Row(html.Div(style={"height": "15px"})),
                    dbc.Row(html.Div(id="coefficients_results")),
                ],
                id="results-coefficients-collapse", 
                is_open=False,
            ),
        ]
    ),
    html.Hr(),
    html.Div([
        dbc.Button(
            "Results Accuracy", 
            id="results_accuracy_button",
            n_clicks=0,
            style={"width": "100%", "display": "block", "margin": "auto"},
        ),
        dbc.Collapse(
            [
                dbc.Row(
                    [
                        html.Div(style={"height": "15px"}),
                        html.Div(id="accuracy_results"),
                    ],
                ),
            ],
            id="results-accuracy-collapse", 
            is_open=False,
        ),
    ]),
    html.Hr(),
    html.Div([
        dbc.Button(
            "Results Efficiency", 
            id="results_efficiency_button",
            n_clicks=0,
            style={"width": "100%", "display": "block", "margin": "auto"}, 
        ),
        dbc.Collapse(
            [
                dbc.Row(
                    [
                        html.Div(style={"height": "15px"}),
                        html.Div(id="efficiency_results"),
                    ],
                ),
            ],
            id="results-efficiency-collapse", 
            is_open=False,
        ),
    ]),
    html.Hr(),
    html.Div([
        dbc.Button(
            "Results Histogram", 
            id="results_histogram_button",
            n_clicks=0,
            style={"width": "100%", "display": "block", "margin": "auto"}, 
        ),
        dbc.Collapse(
            [
                html.Div(style={"height": "15px"}),
                buttons_for_test_histo_voltage_choice(),
                html.Div(style={"height": "15px"}),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("Accuracy of the Histogram (number of x-axis division)"),
                        dbc.Input(id="HistNumberOfXAxisDivision", valid=False, invalid=False, persistence_type='memory', persistence=True),
                    ]
                ),
                dbc.Row(
                    [
                        html.Div(style={"height": "15px"}),
                        html.Div(id="histogram_results"),
                    ],
                ),
            ],
            id="results-histogram-collapse", 
            is_open=False,
        ),
    ]),
    html.Hr(),
    ResultsReportCard,
])
