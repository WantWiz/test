"""
This app creates several cards that allow setting up the test bench. 
"""

#####################################################################################
#                             Imports / Initializations                             #
#####################################################################################

import dash, re
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, dcc, html, callback, State
from sklearn import datasets
from sklearn.cluster import KMeans
from dash.exceptions import PreventUpdate
import Settings, json
import numpy as np
import markdown_test_info
import os, csv, serial, pyvisa, time, sys

# initialize some variables so that the initialization of the setup_page can be done
if ("LowLeg" not in locals() and "TestName" not in locals() and "VHighTab_V" not in locals() and "BoardSN" not in locals()) and "converter_values_tab" not in locals() and "TestIndex" not in locals():
    LowLeg = ""
    TestName = ""
    VHighTab_V = []
    BoardSN = ""
    converter_values_tab = []
    TestIndex = 0

ScriptPath = os.path.dirname('..')
LibFolderName = "Libraries"

LibPath = os.path.join(ScriptPath, LibFolderName)
sys.path.insert(1, LibPath)

import Settings, EAPSI9750, K2000, bk8500, Plot, ActiveLoad, Efficiency, Coefficients, Accuracy, Histogram
import FileMngt, SPIN_Comm, OrganizeDataInCSV

# Check this out https://dash.plotly.com/vtk/click_hover

ResourceManager = pyvisa.ResourceManager()



#####################################################################################
#                                 Test Information                                  #
#####################################################################################

# creation of the card that appears if the test name isn't ok
test_name_issue_card = dbc.Card(
    dbc.CardBody(html.H6("")),
    id="test_name_issue_card"
)

#callbacks that check and update TestName, LowLeg and BoardSN
@callback(
    [
        Output("TestName", "valid"),
        Output("TestName", "invalid"),
        Output("test_name_issue_card", "is_open"),
        Output("test_name_issue_card", "children")
    ],
    [Input("TestName", "n_submit"), Input("TestName", "n_blur")],
    [State("TestName", "value"), State("test_name_issue_card", "is_open")]
)
def validate_test_name(submit_clicks, blur_clicks, value, is_open):
    if value is not None:
        update_JsonTestsHistory()
        if submit_clicks or blur_clicks:
            pattern = r'^[a-zA-Z0-9_-]+$'
            if not re.match(pattern, value):
                return False, True, True, html.H6("Invalid TestName")
            elif value in Settings.JsonTestsHistory_data["TestNamesHistory"]:
                return False, True, True, html.H6("TestName already exists")
            else:
                global TestName
                TestName = value
                return True, False, False, html.H6("")
        return False, False, False, html.H6("")
    return False, False, False, html.H6("")

@callback(
    Output("LowLeg", "valid"),
    [Input("LowLeg", "value")]
)
def update_lowleg_validity(value):
    global LowLeg
    if value is not None:
        LowLeg = int(value)
        return True
    else:
        return False

@callback(
    dash.dependencies.Output("BoardSN", "valid"),
    dash.dependencies.Output("BoardSN", "invalid"),
    [dash.dependencies.Input("BoardSN", "value")]
)
def update_boardsn_validity(value):
    global BoardSN
    if value is not None:
        if value.isdigit() and int(value)>=0:
            BoardSN = int(value)
            return True, False
        else:
            return False, True
    return False, False



#####################################################################################
#                                  Instrument Setup                                 #
#####################################################################################

# initialization of the list of dictionary DMMDict containing the DMM addresses associated with what they measure 
DMMDict = [{'Meas':'IHigh', 'DMM address' : None},
           {'Meas':'VHigh', 'DMM address' : None},
           {'Meas':'ILow', 'DMM address' : None},
           {'Meas':'VLow', 'DMM address' : None}]

# transformation of the dictionary into a dataframe
DMM_store =	pd.DataFrame.from_dict(DMMDict)

# creation of the cards that allow the connections with the DMM and the callbacks that update the DMM address
# associated with the measure of a parameter (IHigh; VHigh; ILow; VLow)
voltage_high = dbc.Card(
    [
        dbc.CardHeader("High_Side Voltage (VHigh)"),
        
        dbc.CardBody([
            html.Div(
                [
                    dbc.Label("DMM Type"),
                    dcc.Dropdown(
                        id="vhigh_dmm_type",
                        options=[
                            {"label": "Keithley2000 address 1", "value": 1},
                            {"label": "Keithley2000 address 2", "value": 2},
                            {"label": "Keithley2000 address 3", "value": 3},
                            {"label": "Keithley2000 address 4", "value": 4}
                        ],
                        value=2
                    ),
                    html.P(),                    
                    dbc.Button(children ="Not Connected", id="vhigh_button", color="danger"),
                ]
            ),
        ]),        
    ],
    id="vhighCard", color = "danger", outline = True
)

@callback(
    Output("vhigh_dmm-type", "children"),
    Input("vhigh_dmm-type", "value"),
    State("vhigh_dmm-type", "value")
)
def update_VHigh_DMM_ad(selected_value, past_value):
    if selected_value:
        Settings.VHighGPIBAddress='GPIB0::' + str(selected_value) + '::INSTR'
    if selected_value is not None:
        value=int(selected_value)
    else:
        value=past_value
    return value

current_high = dbc.Card(
    [
        dbc.CardHeader("High_Side Current (IHigh)"),
        
        dbc.CardBody([
            html.Div(
                [
                    dbc.Label("DMM Type"),
                    dcc.Dropdown(
                        id="ihigh_dmm_type",
                        options=[
                            {"label": "Keithley2000 address 1", "value": 1},
                            {"label": "Keithley2000 address 2", "value": 2},
                            {"label": "Keithley2000 address 3", "value": 3},
                            {"label": "Keithley2000 address 4", "value": 4}
                        ],
                        value=1,
                    ),
                    html.P(),                    
                    dbc.Button("Not Connected", id="ihigh_button", color="danger"),
                ]
            ),
        ]),        
    ],
    id="ihighCard", color = "danger", outline = True
)

@callback(
    Output("ihigh_dmm_type", "value"),
    Input("ihigh_dmm_type", "value"),
    State("ihigh_dmm_type", "value")
)
def update_IHigh_DMM_ad(selected_value, past_value):
    if selected_value:
        Settings.IHighGPIBAddress='GPIB0::' + str(selected_value) + '::INSTR'
    if selected_value is not None:
        value=int(selected_value)
    else:
        value=past_value
    return value

voltage_low = dbc.Card(
    [
        dbc.CardHeader("Low_Side Voltage (VLowX)"),
        
        dbc.CardBody([
            html.Div(
                [
                    dbc.Label("DMM Type"),
                    dcc.Dropdown(
                        id="vlow_dmm_type",
                        options=[
                            {"label": "Keithley2000 address 1", "value": 1},
                            {"label": "Keithley2000 address 2", "value": 2},
                            {"label": "Keithley2000 address 3", "value": 3},
                            {"label": "Keithley2000 address 4", "value": 4}
                        ],
                        value=3,
                    ),
                    html.P(),                    
                    dbc.Button("Not Connected", id="vlow_button", color="danger"),
                ]
            ),
        ]),        
    ],
    id="vlowCard", color = "danger", outline = True
)

@callback(
    Output("vlow_dmm_type", "value"),
    Input("vlow_dmm_type", "value"),
    State("vlow_dmm_type", "value")
)
def update_VLow_DMM_ad(selected_value, past_value):
    if selected_value:
        Settings.VLowGPIBAddress='GPIB0::' + str(selected_value) + '::INSTR'
    if selected_value is not None:
        value=int(selected_value)
    else:
        value=past_value
    return value

current_low = dbc.Card(
    [
        dbc.CardHeader("Low_Side Current (ILowX)"),
       
        dbc.CardBody([
            html.Div(
                [
                    dbc.Label("DMM Type"),
                    dcc.Dropdown(
                        id="ilow_dmm_type",
                        options=[
                            {"label": "Keithley2000 address 1", "value": 1},
                            {"label": "Keithley2000 address 2", "value": 2},
                            {"label": "Keithley2000 address 3", "value": 3},
                            {"label": "Keithley2000 address 4", "value": 4}
                        ],
                        value=4,
                    ),
                    html.P(),                    
                    dbc.Button("Not Connected", id="ilow_button", color="danger"),
                ]
            ),
        ]),        
    ],
    id="ilowCard", color = "danger", outline = True
)

@callback(
    Output("ilow_dmm_type", "value"),
    Input("ilow_dmm_type", "value"),
    State("ilow_dmm_type", "value")
)
def update_ILow_DMM_ad(selected_value, past_value):
    if selected_value:
        Settings.ILowGPIBAddress='GPIB0::' + str(selected_value) + '::INSTR'
    if selected_value is not None:
        value=int(selected_value)
    else:
        value=past_value
    return value

DMMs_on_the_same_ad_card=dbc.Card(
    dbc.CardBody(html.H6("")),
    id="DMMs_on_the_same_ad_card"
)

@callback(
    [
        Output("DMMs_on_the_same_ad_card", "is_open"),
        Output("DMMs_on_the_same_ad_card", "children")
    ],
    [
        Input("ilow_dmm_type", "value"), 
        Input("vlow_dmm_type", "value"),
        Input("ihigh_dmm_type", "value"), 
        Input("vhigh_dmm_type", "value")
     ],
    [State("DMMs_on_the_same_ad_card", "is_open"),
     State("DMMs_on_the_same_ad_card", "children")]
)
def check_DMMs_on_the_same_ad_card(ilow_dmm_type, vlow_dmm_type, ihigh_dmm_type, vhigh_dmm_type, is_open, DMMs_on_the_same_ad_card_children):
    if ilow_dmm_type or vlow_dmm_type or ihigh_dmm_type or vhigh_dmm_type:
        if ((ilow_dmm_type == vlow_dmm_type) or (ilow_dmm_type == ihigh_dmm_type) or (ilow_dmm_type == vhigh_dmm_type) 
            or (vlow_dmm_type == ihigh_dmm_type) or (vlow_dmm_type == vhigh_dmm_type) or (ihigh_dmm_type == vhigh_dmm_type)):
            return True, html.H6("Two DMMs are on the same address")
        return False, html.H6("")
    return is_open, DMMs_on_the_same_ad_card_children

# callback that open/close intrument card
@callback(
          dash.dependencies.Output("instrument_collapse", "is_open"),
          [dash.dependencies.Input("instrument_button", "n_clicks"),
           Input("close_instrument_collapse_button", "n_clicks")],           
          [dash.dependencies.State("instrument_collapse", "is_open")],                   
)
def toggle_instruments_collapse(n_open, n_close, is_open):
    triggered_id = dash.callback_context.triggered_id
    if triggered_id == "instrument_button":
        return True
    if triggered_id == "close_instrument_collapse_button":
        return False
    return is_open

# callback that check and update the connection of DMMs depending on on which button the user clicked
@callback(
    Output("connect_all_DMM_button", "color"),
    Output("connect_all_DMM_button", "children"),
    Output("vlow_button", "color"),
    Output("vlowCard", "color"),
    Output("vlow_button", "children"),
    Output("ilow_button", "color"),
    Output("ilowCard", "color"),
    Output("ilow_button", "children"),
    Output("vhigh_button", "color"),
    Output("vhighCard", "color"),
    Output("vhigh_button", "children"),
    Output("ihigh_button", "color"),
    Output("ihighCard", "color"),
    Output("ihigh_button", "children"),
    Input("connect_all_DMM_button", "n_clicks"),
    Input("vlow_button", "n_clicks"),
    Input("ilow_button", "n_clicks"),
    Input("vhigh_button", "n_clicks"),
    Input("ihigh_button", "n_clicks"),
     [State("connect_all_DMM_button", "color"),
      State("vhigh_button", "color"),
      State("ihigh_button", "color"),
      State("vlow_button", "color"),
      State("ilow_button", "color"),
      State("connect_all_DMM_button", "children"),
      State("vhigh_button", "children"),
      State("ihigh_button", "children"),
      State("vlow_button", "children"),
      State("ilow_button", "children"),
      State("vlowCard", "color"),
      State("vhighCard", "color"),
      State("ilowCard", "color"),
      State("ihighCard", "color"),
      ]
)
def connect_all_DMM(n_all, n_vhigh, n_ihigh, n_vlow, n_ilow, connect_all_DMM_button_color,
                    vhigh_button_color, ihigh_button_color, vlow_button_color, ilow_button_color, connect_all_DMM_button_children, 
                    vhigh_button_children, ihigh_button_children, vlow_button_children, ilow_button_children, 
                    vlowCard_color, vhighCard_color, ilowCard_color, ihighCard_color,
                    ):
    if n_all is None and n_vlow is None and n_ilow is None and n_vhigh is None and n_ihigh is None:
        raise PreventUpdate
    else:
        triggered_id = dash.callback_context.triggered_id
        if triggered_id == "connect_all_DMM_button":
            filtered = DMM_store.query('Meas == "VHigh"')     
            filtered['DMM address'] = hex(id(K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.VHighGPIBAddress))))
            filtered = DMM_store.query('Meas == "IHigh"')     
            filtered['DMM address'] = hex(id(K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.IHighGPIBAddress))))
            filtered = DMM_store.query('Meas == "ILow"')     
            filtered['DMM address'] = hex(id(K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.ILowGPIBAddress))))
            filtered = DMM_store.query('Meas == "VLow"')     
            filtered['DMM address'] = hex(id(K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.VLowGPIBAddress))))
            return "success", "All DMM Connected", "success", "success", "Connected", "success", "success", "Connected", "success", "success", "Connected", "success", "success", "Connected"
        elif triggered_id == "vlow_button":
            filtered = DMM_store.query('Meas == "VLow"')     
            filtered['DMM address'] = hex(id(K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.VLowGPIBAddress))))
            if (vhigh_button_color, ihigh_button_color, ilow_button_color)==(3*("success", )):
                return "success", "All DMM Connected", "success", "success", "Connected", "success", "success", "Connected", "success", "success", "Connected", "success", "success", "Connected"
            return connect_all_DMM_button_color, connect_all_DMM_button_children, "success", "success", "Connected", ilow_button_color, ilowCard_color, ilow_button_children, vhigh_button_color, vhighCard_color, vhigh_button_children,ihigh_button_color, ihighCard_color, ihigh_button_children
        elif triggered_id == "ilow_button":
            filtered = DMM_store.query('Meas == "ILow"')     
            filtered['DMM address'] = hex(id(K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.ILowGPIBAddress))))
            if (vhigh_button_color, ihigh_button_color, vlow_button_color)==(3*("success", )):
                return "success", "All DMM Connected", "success", "success", "Connected", "success", "success", "Connected", "success", "success", "Connected", "success", "success", "Connected"
            return connect_all_DMM_button_color, connect_all_DMM_button_children, vlow_button_color, vlowCard_color, vlow_button_children, "success", "succes", "Connected", vhigh_button_color, vhighCard_color, vhigh_button_children,ihigh_button_color, ihighCard_color, ihigh_button_children
        elif triggered_id == "ihigh_button":
            filtered = DMM_store.query('Meas == "IHigh"')     
            filtered['DMM address'] = hex(id(K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.IHighGPIBAddress))))
            if (vhigh_button_color, vlow_button_color, ilow_button_color)==(3*("success", )):
                return "success", "All DMM Connected", "success", "success", "Connected", "success", "success", "Connected", "success", "success", "Connected", "success", "success", "Connected"
            return connect_all_DMM_button_color, connect_all_DMM_button_children, vlow_button_color, vlowCard_color, vlow_button_children, ilow_button_color, ilowCard_color, ilow_button_children, vhigh_button_color, vhighCard_color, vhigh_button_children, "success", "success", "Connected"
        elif triggered_id == "vhigh_button":
            filtered = DMM_store.query('Meas == "VHigh"')     
            filtered['DMM address'] = hex(id(K2000.KEITHLEY2000(ResourceManager.open_resource(Settings.VHighGPIBAddress))))
            if (ihigh_button_color, vlow_button_color, ilow_button_color)==(3*("success", )):
                return "success", "All DMM Connected", "success", "success", "Connected", "success", "success", "Connected", "success", "success", "Connected", "success", "success", "Connected"
            return connect_all_DMM_button_color, connect_all_DMM_button_children, vlow_button_color, vlowCard_color, vlow_button_children, ilow_button_color, ilowCard_color, ilow_button_children, "success", "success", "Connected", ihigh_button_color, ihighCard_color, ihigh_button_children
 
# callbacks that update instrument_button when all DMMs are connected
@callback(
        Output("instrument_button", "children"),
        Output("instrument_button", "color"),
        Input("vhigh_button", "color"),
        Input("ihigh_button", "color"),
        Input("vlow_button", "color"),
        Input("ilow_button", "color"),
        Input("DMMs_on_the_same_ad_card", "is_open")
)
def all_DMM_connected(vhigh_button_color, ihigh_button_color, vlow_button_color, ilow_button_color, DMMs_on_the_same_ad_card_is_open):
    if vhigh_button_color == "success" and ihigh_button_color == "success" and vlow_button_color and ilow_button_color == "success" and not DMMs_on_the_same_ad_card_is_open:
        return "Instrument Setup completed", "success"
    else:
        return "Instrument Setup", "danger"

# callback that open/close the modal that provides information concerning the instrument setup
@callback(
    Output("DMM_address_modal", "is_open"),
    [Input("DMM_address_info_button", "n_clicks"), Input("DMM_address_modal_close", "n_clicks")],
    [State("DMM_address_modal", "is_open")],
)
def toggle_DMM_address_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# callback that display the content of the modal from the file markdown_test_info
@callback(  
        Output("DMM_address_modal_content", "children"),
        Input("DMM_address_info_button", "n_clicks")
)
def display_DMM_address_info_modal_content(n):
    if n:
        return dcc.Markdown(markdown_test_info.markdown_DMM_address_info)



#####################################################################################
#                                  Experiment Setup                                 #
#####################################################################################

# creation of the cards that allow the connections with the power card, the voltage source and the active load
power_converter = dbc.Card(
    [
        dbc.CardHeader("Power Converter (DUT)"),
        
        dbc.CardBody([
            html.Div(
                [
                    dbc.Label("Converter Type"),
                    dcc.Dropdown(
                        id="converter_type",
                        options=[
                            {"label": "TWIST 1.2", "value": "TWIST 1.2"},
                            {"label": "TWIST 1.3", "value": "TWIST 1.3"}
                        ],
                        value=None,
                    ),                   
                    html.P(),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Port"),
                            dbc.Input(id="port_power_converter", valid=False, invalid=False, persistence_type='memory', persistence=True),
                        ]
                    ),
                    html.Div(style={"height": "15px"}),                    
                    dbc.Button("Not Connected", id="converter_button", color="danger"),
                ]
            ),
        ]),        
    ],
    id="converterCard", color = "danger", outline = True
)
voltage_source = dbc.Card(
    [
        dbc.CardHeader("Voltage Source"),
        
        dbc.CardBody([
            html.Div(
                [
                    dbc.Label("Power Supply Type"),
                    dcc.Dropdown(
                        id="power_supply_type",
                        options=[
                            {"label": "EAPSI9750", "value": "EAPSI9750"}
                        ],
                        value="EAPSI9750",
                    ),
                    html.P(),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Port"),
                            dbc.Input(id="port_voltage_source", valid=False, invalid=False, persistence_type='memory', persistence=True),
                        ]
                    ),
                    html.Div(style={"height": "15px"}),    
                    dbc.Button("Not Connected", id="power_source_button", color="danger"),                  
                ]
            ),
        ]),        
    ],
    id="powerSourceCard", color = "danger", outline = True
)
load_device = dbc.Card(
    [
        dbc.CardHeader("Load"),
        
        dbc.CardBody([
            html.Div(
                [
                    dbc.Label("Load Type"),
                    dcc.Dropdown(
                        id="load_type",
                        options=[
                            {"label": "Active load IT8512B", "value": "Active load IT8512B"}
                        ],
                        value="Active load IT8512B",
                    ),                   
                    html.P(),
                    dbc.Button("Not Connected", id="load_button", color="danger"),
                ]
            ),
        ]),        
    ],
    id="loadCard", color = "danger", outline = True
)

# callbacks that check the port chosen by the user and update it in Settings.py
# for the load, the user doesn't have to manually change the port, it's automatic
@callback(
    Output("port_power_converter", "valid"),
    Output("port_power_converter", "invalid"),
    [Input("port_power_converter", "n_submit"), Input("port_power_converter", "n_blur")],
    State("port_power_converter", "value")
)
def check_port_power_converter_validity(port_power_converter_n_submit, port_power_converter_n_blur, port_power_converter_value):
    if port_power_converter_value and (port_power_converter_n_submit or port_power_converter_n_blur):
        COM_list=["COM" + str(i) for i in range(1,256)] # possible port windows
        port_list=["/dev/ttyUSB" + str(i) for i in range(1,256)] # possible usb port linux
        if str(port_power_converter_value) in (COM_list + port_list):
            Settings.STLINKCommPort=str(port_power_converter_value)
            return True, False
        return False, True
    return False, False

@callback(
    Output("port_voltage_source", "valid"),
    Output("port_voltage_source", "invalid"),
    [Input("port_voltage_source", "n_submit"), Input("port_voltage_source", "n_blur")],
    State("port_voltage_source", "value")
)
def check_port_voltage_source_validity(port_voltage_source_n_submit, port_voltage_source_n_blur, port_voltage_source_value):
    if port_voltage_source_value and (port_voltage_source_n_submit or port_voltage_source_n_blur):
        COM_list=["COM" + str(i) for i in range(1,256)] # possible port windows
        port_list=["/dev/ttyUSB" + str(i) for i in range(1,256)] # possible usb port linux
        if str(port_voltage_source_value) in (COM_list + port_list):
            Settings.PSUCommPorttmp = str(port_voltage_source_value)
            return True, False
        return False, True
    return False, False

# callback that open/close intrument card
@callback(
          dash.dependencies.Output("experiment_collapse", "is_open"),
          [dash.dependencies.Input("experiment_button", "n_clicks"),
           Input("close_experiment_collapse_button", "n_clicks")],           
          [dash.dependencies.State("experiment_collapse", "is_open")],                   
)
def toggle_experiment_collapse(n_open, n_close, is_open):
    triggered_id = dash.callback_context.triggered_id
    if triggered_id == "experiment_button":
        return True
    if triggered_id == "close_experiment_collapse_button":
        return False
    return is_open

# callback that check and update the connection of the load, the voltage source or the power card depending on on which button the user clicked
@callback(
        dash.dependencies.Output("power_source_button", "color"),
        dash.dependencies.Output("power_source_button", "children"),
        dash.dependencies.Output("converter_button", "color"),
        dash.dependencies.Output("converter_button", "children"),
        dash.dependencies.Output("load_button", "color"),
        dash.dependencies.Output("load_button", "children"),
        dash.dependencies.Output("connect_all_instruments_button", "color"),
        dash.dependencies.Output("connect_all_instruments_button", "children"),
        dash.dependencies.Input("power_source_button", "n_clicks"),
        dash.dependencies.Input("converter_button", "n_clicks"),
        dash.dependencies.Input("load_button", "n_clicks"),
        dash.dependencies.Input("connect_all_instruments_button", "n_clicks"),
        [dash.dependencies.State("power_source_button", "color"),
        dash.dependencies.State("powerSourceCard", "color"),
        dash.dependencies.State("power_source_button", "children"),
        dash.dependencies.State("converter_button", "color"),
        dash.dependencies.State("converterCard", "color"),
        dash.dependencies.State("converter_button", "children"),
        dash.dependencies.State("load_button", "color"),
        dash.dependencies.State("loadCard", "color"),
        dash.dependencies.State("load_button", "children"),
        dash.dependencies.State("connect_all_instruments_button", "color"),
        dash.dependencies.State("connect_all_instruments_button", "children")
        ]
)
def connect_all_instruments(n_pow, n_conv, n_load, n_all, power_source_button_color, powerSourceCard_color, 
                            power_source_button_children, converter_button_color, converterCard_color, 
                            converter_button_children, load_button_color, loadCard_color, load_button_children,
                            connect_all_instruments_button_color, connect_all_instruments_button_children):
    if n_pow is None and n_conv is None and n_load is None and n_all is None:
        raise PreventUpdate
    else:
        triggered_id = dash.callback_context.triggered_id
        if triggered_id == "connect_all_instruments_button":
            ActiveLoadObj = serial.Serial(Settings.ActiveLoadCommPort)
            STLINK = serial.Serial(Settings.STLINKCommPort)
            PowerSupply = EAPSI9750.EAPSI9750(ResourceManager.open_resource(Settings.PSUCommPort))
            return "success", "Connected", "success", "Connected", "success", "Connected", "success", "All Instruments Connected"
        elif triggered_id == "power_source_button":
            PowerSupply = EAPSI9750.EAPSI9750(ResourceManager.open_resource(Settings.PSUCommPort))
            if converter_button_color=="success" and  load_button_color=="success":
                return "success", "Connected", converter_button_color, converter_button_children, load_button_color, load_button_children, "success", "All Instruments Connected"
            return "success", "Connected", converter_button_color, converter_button_children, load_button_color, load_button_children, connect_all_instruments_button_color, connect_all_instruments_button_children
        elif triggered_id == "converter_button":
            STLINK = serial.Serial(Settings.STLINKCommPort)
            if power_source_button_color=="success" and  load_button_color=="success":
                return power_source_button_color, power_source_button_children, "success", "Connected", load_button_color, load_button_children, "success", "All Instruments Connected",
            return power_source_button_color, power_source_button_children, "success", "Connected", load_button_color, load_button_children, connect_all_instruments_button_color, connect_all_instruments_button_children
        elif triggered_id == "load_button":
            ActiveLoadObj = serial.Serial(Settings.ActiveLoadCommPort)
            if power_source_button_color=="success" and converter_button_color=="success":
                return power_source_button_color, power_source_button_children, converter_button_color, converter_button_children, "success", "Connected", "success", "All Instruments Connected"
            return power_source_button_color, power_source_button_children, converter_button_color, converter_button_children, "success", "Connected", connect_all_instruments_button_color, connect_all_instruments_button_children

# callback that update the color of the cards when the device is connected and its type is chosen
@callback(
        dash.dependencies.Output("powerSourceCard", "color"),
        dash.dependencies.Output("converterCard", "color"),
        dash.dependencies.Output("loadCard", "color"),
        dash.dependencies.Input("converter_type", "value"),
        dash.dependencies.Input("load_type", "value"),
        dash.dependencies.Input("power_supply_type", "value"),
        dash.dependencies.Input("converter_button", "color"),
        dash.dependencies.Input("load_button", "color"),
        dash.dependencies.Input("power_source_button", "color"),       
        [dash.dependencies.State("powerSourceCard", "color"),
        dash.dependencies.State("converterCard", "color"),
        dash.dependencies.State("loadCard", "color")]
)
def update_exp_card_color(converter_type_value, load_type_value, power_supply_type_value, converter_button_color, load_button_color, power_source_button_color,
                          powerSourceCard_color, converterCard_color, loadCard_color):
    if converter_type_value is not None and converter_button_color=="success":
        converterCard_color = "success"
    if load_type_value is not None and load_button_color=="success":
        loadCard_color="success"
    if power_supply_type_value is not None and power_source_button_color=="success":
        powerSourceCard_color="success"
    return powerSourceCard_color, converterCard_color, loadCard_color

# callbacks that update experiment_button when the load, the voltage source and the power card are connected
@callback(
    Output("experiment_button", "color"),
    Output("experiment_button", "children"), 
    Input("load_button", "color"),
    Input("converter_button", "color"),
    Input("power_source_button", "color"),
    Input("save_all_parameters_button", "children"),
    Input("converter_type", "value"),
    Input("load_type", "value"),
    Input("power_supply_type", "value"),
)
def exp_setup_completed(load_button_color, converter_button_color, power_source_button_color, save_all_parameters_button_children, converter_type_value, load_type_value, power_supply_type_value):
    if (load_button_color == "success" and converter_button_color == "success" and power_source_button_color == "success" and save_all_parameters_button_children == "All parameters saved"
        and converter_type_value is not None and load_type_value is not None and power_supply_type_value is not None):
        return "success", "Experiment Setup Completed"
    else :
        return "danger", "Experiment Setup"

# creation of the InputText to configure the global parameters for the tests
Global_Parameters = dbc.Card(
            [
                dbc.CardHeader(
                    html.A(
                        "Global parameters",
                        id="global_parameters_card_header",
                        className="global_parameters_card_header",
                        style={"textDecoration": "none", "cursor": "pointer"},
                    )
                ),
                dbc.Collapse(
                    dbc.CardBody(
                        [
                        dbc.Button(html.I(className="fas fa-lightbulb", style={"margin_right": "4px"})
                                   , id="info_global_parameters", outline=True, n_clicks=0),
                        dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("Information global parameters")),
                            dbc.ModalBody(id="info_global_parameters_modal_content"),
                            dbc.ModalFooter(
                                dbc.Button(
                                    "Close", id="info_global_parameters_modal_close", className="ms_auto", n_clicks=0
                                )
                            ),
                        ],
                        id="info_global_parameters_modal",
                        size="lg",
                        is_open=False,
                        ),

                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Maximum current the load will accept to sink (A)"),
                                    dbc.Input(id="LoadInternalSafetyCurrent_A", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Maximum power the load will accept to sink (W)"),
                                    dbc.Input(id="LoadInternalSafetyPower_W", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Number of samples read per duty (DMM and SPIN)"),
                                    dbc.Input(id="NumberOfPointsPerDuty", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Step of duty cycle (percent)"),
                                    dbc.Input(id="duty_step_Percent", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Starting duty cycle (percent)"),
                                    dbc.Input(id="starting_duty_cycle_Percent", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            html.H6(
                                "Change the core and flash the card with the values of starting duty and duty step you want (if differents form default ones)"
                            ),
                        ]
                    ),
                    id="global_parameters_card_collapse",
                ),
            ],
            id="global_parameters_card", color = "", outline = True
        )

# callback that open/close the modal that provides information concerning the the global parameters
@callback(
    Output("info_global_parameters_modal", "is_open"),
    [Input("info_global_parameters", "n_clicks"), Input("info_global_parameters_modal_close", "n_clicks")],
    [State("info_global_parameters_modal", "is_open")],
)
def toggle_info_global_parameters_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# callback that display the content of the modal from the file markdown_test_info
@callback(  
        Output("info_global_parameters_modal_content", "children"),
        Input("info_global_parameters", "n_clicks")
)
def display_info_global_parameters_modal_content(n):
    if n:
        return dcc.Markdown(markdown_test_info.markdown_info_global_parameters)

# callbacks that update the validity of the global parameters input
@callback(
    Output("NumberOfStepInDutySweep", "valid"),
    Output("NumberOfStepInDutySweep", "invalid"),
    [Input("NumberOfStepInDutySweep", "n_submit"), Input("NumberOfStepInDutySweep", "n_blur")],
    State("NumberOfStepInDutySweep", "value")
)
def check_NumberOfStepInDutySweep_validity(NumberOfStepInDutySweep_n_submit, NumberOfStepInDutySweep_n_blur, NumberOfStepInDutySweep_value):
    if NumberOfStepInDutySweep_value and (NumberOfStepInDutySweep_n_submit or NumberOfStepInDutySweep_n_blur):
        if str(NumberOfStepInDutySweep_value).isdigit() and int(NumberOfStepInDutySweep_value) >= 1 and int(NumberOfStepInDutySweep_value) <= 1000:
            return True, False
        return False, True
    return False, False

@callback(
    Output("LoadInternalSafetyCurrent_A", "valid"),
    Output("LoadInternalSafetyCurrent_A", "invalid"),
    [Input("LoadInternalSafetyCurrent_A", "n_submit"), Input("LoadInternalSafetyCurrent_A", "n_blur")],
    State("LoadInternalSafetyCurrent_A", "value")
)
def check_LoadInternalSafetyCurrent_A_validity(LoadInternalSafetyCurrent_A_n_submit, LoadInternalSafetyCurrent_A_n_blur, LoadInternalSafetyCurrent_A_value):
    if LoadInternalSafetyCurrent_A_value and (LoadInternalSafetyCurrent_A_n_submit or LoadInternalSafetyCurrent_A_n_blur):
        if str(LoadInternalSafetyCurrent_A_value).isdigit() and int(LoadInternalSafetyCurrent_A_value) >= 1 and int(LoadInternalSafetyCurrent_A_value) <= 15:
            return True, False
        return False, True
    return False, False

@callback(
    Output("LoadInternalSafetyPower_W", "valid"),
    Output("LoadInternalSafetyPower_W", "invalid"),
    [Input("LoadInternalSafetyPower_W", "n_submit"), Input("LoadInternalSafetyPower_W", "n_blur")],
    State("LoadInternalSafetyPower_W", "value")
)
def check_LoadInternalSafetyPower_W_validity(LoadInternalSafetyPower_W_n_submit, LoadInternalSafetyPower_W_n_blur, LoadInternalSafetyPower_W_value):
    if LoadInternalSafetyPower_W_value and (LoadInternalSafetyPower_W_n_submit or LoadInternalSafetyPower_W_n_blur):
        if str(LoadInternalSafetyPower_W_value).isdigit() and int(LoadInternalSafetyPower_W_value) >= 0 and int(LoadInternalSafetyPower_W_value) <= 300:
            return True, False
        return False, True
    return False, False

@callback(
    Output("NumberOfPointsPerDuty", "valid"),
    Output("NumberOfPointsPerDuty", "invalid"),
    [Input("NumberOfPointsPerDuty", "n_submit"), Input("NumberOfPointsPerDuty", "n_blur")],
    State("NumberOfPointsPerDuty", "value")
)
def check_NumberOfPointsPerDuty_validity(NumberOfPointsPerDuty_n_submit, NumberOfPointsPerDuty_n_blur, NumberOfPointsPerDuty_value):
    if NumberOfPointsPerDuty_value and (NumberOfPointsPerDuty_n_submit or NumberOfPointsPerDuty_n_blur):
        if str(NumberOfPointsPerDuty_value).isdigit() and int(NumberOfPointsPerDuty_value) >= 1 and int(NumberOfPointsPerDuty_value) <= 1000:
            return True, False
        return False, True
    return False, False

@callback(
    Output("duty_step_Percent", "valid"),
    Output("duty_step_Percent", "invalid"),
    [Input("duty_step_Percent", "n_submit"), Input("duty_step_Percent", "n_blur")],
    State("duty_step_Percent", "value")
)
def check_duty_step_Percent_validity(duty_step_Percent_n_submit, duty_step_Percent_n_blur, duty_step_Percent_value):
    if duty_step_Percent_value and (duty_step_Percent_n_submit or duty_step_Percent_n_blur):
        if str(duty_step_Percent_value).isdigit() and int(duty_step_Percent_value) > 0 and int(duty_step_Percent_value) <= 50:
            return True, False
        return False, True
    return False, False

@callback(
    Output("starting_duty_cycle_Percent", "valid"),
    Output("starting_duty_cycle_Percent", "invalid"),
    [Input("starting_duty_cycle_Percent", "n_submit"), Input("starting_duty_cycle_Percent", "n_blur")],
    State("starting_duty_cycle_Percent", "value")
)
def check_starting_duty_cycle_Percent_validity(starting_duty_cycle_Percent_n_submit, starting_duty_cycle_Percent_n_blur, starting_duty_cycle_Percent_value):
    if starting_duty_cycle_Percent_value and (starting_duty_cycle_Percent_n_submit or starting_duty_cycle_Percent_n_blur):
        if str(starting_duty_cycle_Percent_value).isdigit() and int(starting_duty_cycle_Percent_value) > 0 and int(starting_duty_cycle_Percent_value) <= 100:
            return True, False
        return False, True
    return False, False

# callbacks that open/close the global parameters card
@callback(
    Output("global_parameters_card_collapse", "is_open"),
    [Input("global_parameters_card_header", "n_clicks")],
    [dash.dependencies.State("global_parameters_card_collapse", "is_open")],
)
def toggle_global_parameters_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# callbacks that update the color of the global parameters card
@callback(
        Output("global_parameters_card", "color"),
        Input("LoadInternalSafetyCurrent_A", "valid"),
        Input("LoadInternalSafetyPower_W", "valid"),
        Input("NumberOfPointsPerDuty", "valid"),
        Input("duty_step_Percent", "valid"),
        Input("starting_duty_cycle_Percent", "valid"),
        Input("LoadInternalSafetyCurrent_A", "invalid"),
        Input("LoadInternalSafetyPower_W", "invalid"),
        Input("NumberOfPointsPerDuty", "invalid"),
        Input("duty_step_Percent", "invalid"),
        Input("starting_duty_cycle_Percent", "invalid"),
        Input("LoadInternalSafetyCurrent_A", "value"),
        Input("LoadInternalSafetyPower_W", "value"),
        Input("NumberOfPointsPerDuty", "value"),
        Input("duty_step_Percent", "value"),
        Input("starting_duty_cycle_Percent", "value"),
        Input("TestNamesLoadParameters", "valid")
)
def update_global_parameters_card_color(LoadInternalSafetyCurrent_A_validity, LoadInternalSafetyPower_W_validity, 
                                        NumberOfPointsPerDuty_validity, duty_step_Percent_validity, starting_duty_cycle_Percent_validity,
                                        LoadInternalSafetyCurrent_A_invalidity, LoadInternalSafetyPower_W_invalidity, 
                                        NumberOfPointsPerDuty_invalidity, duty_step_Percent_invalidity, starting_duty_cycle_Percent_invalidity,
                                        LoadInternalSafetyCurrent_A_value, LoadInternalSafetyPower_W_value, 
                                        NumberOfPointsPerDuty_value, duty_step_Percent_value, starting_duty_cycle_Percent_value,
                                        TestNamesLoadParameters_validity):
    if ((LoadInternalSafetyCurrent_A_validity and LoadInternalSafetyPower_W_validity and NumberOfPointsPerDuty_validity and duty_step_Percent_validity and starting_duty_cycle_Percent_validity) or (TestNamesLoadParameters_validity and not (
        LoadInternalSafetyCurrent_A_invalidity or LoadInternalSafetyPower_W_invalidity or NumberOfPointsPerDuty_invalidity or duty_step_Percent_invalidity or starting_duty_cycle_Percent_invalidity) and 
                                                LoadInternalSafetyCurrent_A_value !="" and LoadInternalSafetyPower_W_value !="" and
                                        NumberOfPointsPerDuty_value !="" and duty_step_Percent_value !="" and starting_duty_cycle_Percent_value !="")):
        return "success"
    return ""




#####################################################################################
#                     Json Tests History & test pameters data                       #
#####################################################################################

# update JsonTestsHistory.py according to the existing folders
# if a name in JsonTestsHistory.py is not an existing folder in Results, he is removed from JsonTestsHistory.py
def lister_fichiers_dossier(PathFolder):
    try:
        FilesList = os.listdir(PathFolder)
        return FilesList
    except FileNotFoundError:
        return []
def update_JsonTestsHistory():
    # path of the folder results
    Dir = os.path.dirname(os.path.abspath(__file__))
    Dir = os.path.dirname(Dir)
    PathFolder = os.path.join(Dir, "Results")
    FilesList = lister_fichiers_dossier(PathFolder)

    TestNamesHistory = Settings.JsonTestsHistory_data["TestNamesHistory"].copy()
    # delete defaultparameters
    del TestNamesHistory[0]
    # find the index of the tests that don't have a folder associated
    TestsIndex = []
    for test in TestNamesHistory:
        if test not in FilesList:
            TestsIndex.append(TestNamesHistory.index(test))
    for i in TestsIndex:
        Settings.JsonTestsHistory_data["TestNamesHistory"][i+1] = 0
        Settings.JsonTestsHistory_data["BoardSNHistory"][i+1] = 0
        Settings.JsonTestsHistory_data["LowLegHistory"][i+1] = 0
        Settings.JsonTestsHistory_data["EffVHighStepArray_V_History"][i+1] = 0
        Settings.JsonTestsHistory_data["TestsDoneHistory"][i+1] = 0
        Settings.JsonTestsHistory_data["LoadTypeHistory"][i+1] = 0
        Settings.JsonTestsHistory_data["PowerSupplyTypeHistory"][i+1] = 0
        Settings.JsonTestsHistory_data["ConverterTypeHistory"][i+1] = 0
        Settings.JsonTestsHistory_data["HistVHighStepArray_mV_history"][i+1] = 0

    Settings.JsonTestsHistory_data["TestNamesHistory"] = [i for i in Settings.JsonTestsHistory_data["TestNamesHistory"] if i !=0]
    Settings.JsonTestsHistory_data["BoardSNHistory"] = [i for i in Settings.JsonTestsHistory_data["BoardSNHistory"] if i !=0]
    Settings.JsonTestsHistory_data["LowLegHistory"] = [i for i in Settings.JsonTestsHistory_data["LowLegHistory"] if i !=0]
    Settings.JsonTestsHistory_data["EffVHighStepArray_V_History"] = [i for i in Settings.JsonTestsHistory_data["EffVHighStepArray_V_History"] if i !=0]
    Settings.JsonTestsHistory_data["TestsDoneHistory"] = [i for i in Settings.JsonTestsHistory_data["TestsDoneHistory"] if i !=0]
    Settings.JsonTestsHistory_data["LoadTypeHistory"] = [i for i in Settings.JsonTestsHistory_data["LoadTypeHistory"] if i !=0]
    Settings.JsonTestsHistory_data["PowerSupplyTypeHistory"] = [i for i in Settings.JsonTestsHistory_data["PowerSupplyTypeHistory"] if i !=0]
    Settings.JsonTestsHistory_data["ConverterTypeHistory"] = [i for i in Settings.JsonTestsHistory_data["ConverterTypeHistory"] if i !=0]
    Settings.JsonTestsHistory_data["HistVHighStepArray_mV_history"] = [i for i in Settings.JsonTestsHistory_data["HistVHighStepArray_mV_history"] if i !=0]
    with open("JsonTestsHistory.json", "w") as f:
        json.dump(Settings.JsonTestsHistory_data, f, indent=4)
update_JsonTestsHistory()

# callback that allow the save of all parameters (if they are all valid) when the user clicks on the button associated
@callback(
        Output("save_all_parameters_button", "children"),
        Output("save_all_parameters_button", "color"),
        dash.dependencies.Input("save_all_parameters_button", "n_clicks"),
        dash.dependencies.State("LoadInternalSafetyCurrent_A", "value"),
        dash.dependencies.State("LoadInternalSafetyPower_W", "value"),
        dash.dependencies.State("NumberOfPointsPerDuty", "value"),
        dash.dependencies.State("duty_step_Percent", "value"),
        dash.dependencies.State("NumberOfStepInDutySweep", "value"),
        dash.dependencies.State("starting_duty_cycle_Percent", "value"),
        dash.dependencies.State("AccVHighCalibrationDutyPercent", "value"),
        dash.dependencies.State("AccVHighCalibrationLowCurrent_mA", "value"),
        dash.dependencies.State("AccIHighCalibrationDuty_Percent", "value"),
        dash.dependencies.State("AccIHighCalibrationVHigh_mV", "value"),
        dash.dependencies.State("AccVLowCalibrationLowCurrent_mA", "value"),
        dash.dependencies.State("AccVLowCalibrationVHigh_mV", "value"),
        dash.dependencies.State("AccILowCalibrationDuty_Percent", "value"),
        dash.dependencies.State("AccILowCalibrationVHigh_mV", "value"),
        dash.dependencies.State("AccNumberOfStepInVLowDutySweep", "value"),
        dash.dependencies.State("AccNumberOfVHighStep", "value"),
        dash.dependencies.State("AccStepMinVHigh_mV", "value"),
        dash.dependencies.State("AccStepMaxVHigh_mV", "value"),
        dash.dependencies.State("AccIHighNumberOfCurrentStep", "value"),
        dash.dependencies.State("AccIHighStepMinCurrent_mA", "value"),
        dash.dependencies.State("AccIHighStepMaxCurrent_mA", "value"),
        dash.dependencies.State("AccILowNumberOfCurrentStep", "value"),
        dash.dependencies.State("AccILowStepMinCurrent_mA", "value"),
        dash.dependencies.State("AccILowStepMaxCurrent_mA", "value"),
        dash.dependencies.State("EffNumberOfVHighStep", "value"),
        dash.dependencies.State("EffStepMinVHigh_mV", "value"),
        dash.dependencies.State("EffStepMaxVHigh_mV", "value"),
        dash.dependencies.State("EffNumberOfIHighStep", "value"),
        dash.dependencies.State("EffStepMinIHigh_mA", "value"),
        dash.dependencies.State("EffStepMaxIHigh_mA", "value"),
        dash.dependencies.State("CoeffNumberOfTWISTMeas", "value"),
        dash.dependencies.State("CoeffVHighCalibrationDutyPercent", "value"),
        dash.dependencies.State("CoeffVHighCalibrationLowCurrent_mA", "value"),
        dash.dependencies.State("CoeffIHighCalibrationDuty_Percent", "value"),
        dash.dependencies.State("CoeffIHighCalibrationVHigh_mV", "value"),
        dash.dependencies.State("CoeffVLowCalibrationLowCurrent_mA", "value"),
        dash.dependencies.State("CoeffVLowCalibrationVHigh_mV", "value"),
        dash.dependencies.State("CoeffILowCalibrationDuty_Percent", "value"),
        dash.dependencies.State("CoeffILowCalibrationVHigh_mV", "value"),
        dash.dependencies.State("CoeffStepMinVHigh_mV", "value"),
        dash.dependencies.State("CoeffStepMaxVHigh_mV", "value"),
        dash.dependencies.State("CoeffNumberOfVHighStep", "value"),
        dash.dependencies.State("CoeffStepMinCurrent_mA", "value"),
        dash.dependencies.State("CoeffStepMaxCurrent_mA", "value"),
        dash.dependencies.State("CoeffNumberOfCurrentStep", "value"),

        dash.dependencies.State("HistNumberOfPointsPerDuty", "value"),
        dash.dependencies.State("HistVHighCalibrationDutyPercent", "value"),
        dash.dependencies.State("HistVHighCalibrationLowCurrent_mA", "value"),
        dash.dependencies.State("HistNumberOfVHighStep", "value"),
        dash.dependencies.State("HistStepMinVHigh_mV", "value"),
        dash.dependencies.State("HistStepMaxVHigh_mV", "value"),

        dash.dependencies.State("TestName", "valid"),
        dash.dependencies.State("BoardSN", "valid"),
        dash.dependencies.State("LowLeg", "valid"),
        dash.dependencies.State("global_parameters_card", "color"),
        dash.dependencies.State("coefficients_test_parameters_card", "color"),
        dash.dependencies.State("efficiency_test_parameters_card", "color"),
        dash.dependencies.State("accuracy_test_parameters_card", "color"),
)
def uptade_all_json_data(n, LoadInternalSafetyCurrent_A_value, LoadInternalSafetyPower_W_value, NumberOfPointsPerDuty_value, 
                     duty_step_Percent_value, NumberOfStepInDutySweep_value, starting_duty_cycle_Percent_value, 
                     AccVHighCalibrationDutyPercent_value, AccVHighCalibrationLowCurrent_mA_value, AccIHighCalibrationDuty_Percent_value, 
                     AccIHighCalibrationVHigh_mV_value, AccVLowCalibrationLowCurrent_mA_value, AccVLowCalibrationVHigh_mV_value, 
                     AccILowCalibrationDuty_Percent_value, AccILowCalibrationVHigh_mV_value, AccNumberOfStepInVLowDutySweep_value, 
                     AccNumberOfVHighStep_value, AccStepMinVHigh_mV_value, AccStepMaxVHigh_mV_value, AccIHighNumberOfCurrentStep_value, 
                     AccIHighStepMinCurrent_mA_value, AccIHighStepMaxCurrent_mA_value, AccILowNumberOfCurrentStep_value, 
                     AccILowStepMinCurrent_mA_value, AccILowStepMaxCurrent_mA_value, EffNumberOfVHighStep_value, 
                     EffStepMinVHigh_mV_value, EffStepMaxVHigh_mV_value, EffNumberOfIHighStep_value, EffStepMinIHigh_mA_value, 
                     EffStepMaxIHigh_mA_value, CoeffNumberOfTWISTMeas_value, 
                     CoeffVHighCalibrationDutyPercent_value, CoeffVHighCalibrationLowCurrent_mA_value,
                     CoeffIHighCalibrationDuty_Percent_value, CoeffIHighCalibrationVHigh_mV_value, CoeffVLowCalibrationLowCurrent_mA_value, 
                     CoeffVLowCalibrationVHigh_mV_value, CoeffILowCalibrationDuty_Percent_value, CoeffILowCalibrationVHigh_mV_value, 
                     CoeffStepMinVHigh_mV_value, CoeffStepMaxVHigh_mV_value, CoeffNumberOfVHighStep_value, CoeffStepMinCurrent_mA_value, 
                     CoeffStepMaxCurrent_mA_value, CoeffNumberOfCurrentStep_value, HistNumberOfPointsPerDuty_value, HistVHighCalibrationDutyPercent_value,
                     HistVHighCalibrationLowCurrent_mA_value, HistNumberOfVHighStep_value, HistStepMinVHigh_mV_value, HistStepMaxVHigh_mV_value,
                     TestName_validity, BoardSN_valididy, LowLeg_validity,
                     global_parameters_card_color, coefficients_test_parameters_card_color, efficiency_test_parameters_card_color, accuracy_test_parameters_card_color):
    if n:
        if (TestName_validity and BoardSN_valididy and LowLeg_validity and (global_parameters_card_color, coefficients_test_parameters_card_color, efficiency_test_parameters_card_color, accuracy_test_parameters_card_color)==4*("success", )):
           
            Settings.json_data["LoadInternalSafetyCurrent_A"] = int(LoadInternalSafetyCurrent_A_value)
            Settings.json_data["LoadInternalSafetyPower_W"] = int(LoadInternalSafetyPower_W_value)
            Settings.json_data["NumberOfPointsPerDuty"] = int(NumberOfPointsPerDuty_value)
            Settings.json_data["duty_step_Percent"] = int(duty_step_Percent_value)
            Settings.json_data["NumberOfStepInDutySweep"] = int(NumberOfStepInDutySweep_value)
            Settings.json_data["starting_duty_cycle_Percent"] = int(starting_duty_cycle_Percent_value)
            Settings.json_data["AccVHighCalibrationDutyPercent"] = int(AccVHighCalibrationDutyPercent_value)
            Settings.json_data["AccVHighCalibrationLowCurrent_mA"] = int(AccVHighCalibrationLowCurrent_mA_value)
            Settings.json_data["AccIHighCalibrationDuty_Percent"] = int(AccIHighCalibrationDuty_Percent_value)
            Settings.json_data["AccIHighCalibrationVHigh_mV"] = int(AccIHighCalibrationVHigh_mV_value)
            Settings.json_data["AccVLowCalibrationLowCurrent_mA"] = int(AccVLowCalibrationLowCurrent_mA_value)
            Settings.json_data["AccVLowCalibrationVHigh_mV"] = int(AccVLowCalibrationVHigh_mV_value)
            Settings.json_data["AccILowCalibrationDuty_Percent"] = int(AccILowCalibrationDuty_Percent_value)
            Settings.json_data["AccILowCalibrationVHigh_mV"] = int(AccILowCalibrationVHigh_mV_value)
            Settings.json_data["AccNumberOfStepInVLowDutySweep"] = int(AccNumberOfStepInVLowDutySweep_value)
            Settings.json_data["AccNumberOfVHighStep"] = int(AccNumberOfVHighStep_value)
            Settings.json_data["AccStepMinVHigh_mV"] = int(AccStepMinVHigh_mV_value)
            Settings.json_data["AccStepMaxVHigh_mV"] = int(AccStepMaxVHigh_mV_value)
            Settings.json_data["AccVHighStepArray_mV"] = np.linspace(Settings.json_data["AccStepMinVHigh_mV"], Settings.json_data["AccStepMaxVHigh_mV"], Settings.json_data["AccNumberOfVHighStep"])
            Settings.json_data["AccVHighStepArray_mV"] = [round(num, 0) for num in  Settings.json_data["AccVHighStepArray_mV"]]
            Settings.json_data["AccIHighNumberOfCurrentStep"] = int(AccIHighNumberOfCurrentStep_value)
            Settings.json_data["AccIHighStepMinCurrent_mA"] = int(AccIHighStepMinCurrent_mA_value)
            Settings.json_data["AccIHighStepMaxCurrent_mA"] = int(AccIHighStepMaxCurrent_mA_value)
            Settings.json_data["AccIHighCurrentStepArray_mA"] = np.linspace(Settings.json_data["AccIHighStepMinCurrent_mA"], Settings.json_data["AccIHighStepMaxCurrent_mA"], Settings.json_data["AccIHighNumberOfCurrentStep"])
            Settings.json_data["AccIHighCurrentStepArray_mA"] = [round(num, 0) for num in Settings.json_data["AccIHighCurrentStepArray_mA"]]
            Settings.json_data["AccILowNumberOfCurrentStep"] = int(AccILowNumberOfCurrentStep_value)
            Settings.json_data["AccILowStepMinCurrent_mA"] = int(AccILowStepMinCurrent_mA_value)
            Settings.json_data["AccILowStepMaxCurrent_mA"] = int(AccILowStepMaxCurrent_mA_value)
            Settings.json_data["AccILowCurrentStepArray_mA"] = np.linspace(Settings.json_data["AccILowStepMinCurrent_mA"], Settings.json_data["AccILowStepMaxCurrent_mA"], Settings.json_data["AccILowNumberOfCurrentStep"])
            Settings.json_data["AccILowCurrentStepArray_mA"] = [round(num, 0) for num in Settings.json_data["AccILowCurrentStepArray_mA"]]
            Settings.json_data["EffNumberOfVHighStep"] = int(EffNumberOfVHighStep_value)
            Settings.json_data["EffStepMinVHigh_mV"] = int(EffStepMinVHigh_mV_value)
            Settings.json_data["EffStepMaxVHigh_mV"] = int(EffStepMaxVHigh_mV_value)
            Settings.json_data["EffVHighStepArray_mV"] = np.linspace(Settings.json_data["EffStepMinVHigh_mV"], Settings.json_data["EffStepMaxVHigh_mV"], Settings.json_data["EffNumberOfVHighStep"])
            Settings.json_data["EffVHighStepArray_mV"] = [round(num, 0) for num in Settings.json_data["EffVHighStepArray_mV"]]
            Settings.json_data["EffNumberOfIHighStep"] = int(EffNumberOfIHighStep_value)
            Settings.json_data["EffStepMinIHigh_mA"] = int(EffStepMinIHigh_mA_value)
            Settings.json_data["EffStepMaxIHigh_mA"] = int(EffStepMaxIHigh_mA_value)
            Settings.json_data["EffIHighStepArray_mA"] = np.linspace(Settings.json_data["EffStepMinIHigh_mA"], Settings.json_data["EffStepMaxIHigh_mA"], Settings.json_data["EffNumberOfIHighStep"])
            Settings.json_data["EffIHighStepArray_mA"] = [round(num, 0) for num in Settings.json_data["EffIHighStepArray_mA"]]      
            Settings.json_data["CoeffNumberOfTWISTMeas"] = int(CoeffNumberOfTWISTMeas_value)
            Settings.json_data["CoeffVHighCalibrationDutyPercent"] = int(CoeffVHighCalibrationDutyPercent_value)
            Settings.json_data["CoeffVHighCalibrationLowCurrent_mA"] = int(CoeffVHighCalibrationLowCurrent_mA_value)
            Settings.json_data["CoeffIHighCalibrationDuty_Percent"] = int(CoeffIHighCalibrationDuty_Percent_value)
            Settings.json_data["CoeffIHighCalibrationVHigh_mV"] = int(CoeffIHighCalibrationVHigh_mV_value)
            Settings.json_data["CoeffVLowCalibrationLowCurrent_mA"] = int(CoeffVLowCalibrationLowCurrent_mA_value)
            Settings.json_data["CoeffVLowCalibrationVHigh_mV"] = int(CoeffVLowCalibrationVHigh_mV_value)
            Settings.json_data["CoeffILowCalibrationDuty_Percent"] = int(CoeffILowCalibrationDuty_Percent_value)
            Settings.json_data["CoeffILowCalibrationVHigh_mV"] = int(CoeffILowCalibrationVHigh_mV_value)
            Settings.json_data["CoeffStepMinVHigh_mV"] = int(CoeffStepMinVHigh_mV_value)
            Settings.json_data["CoeffStepMaxVHigh_mV"] = int(CoeffStepMaxVHigh_mV_value)
            Settings.json_data["CoeffNumberOfVHighStep"] = int(CoeffNumberOfVHighStep_value)
            Settings.json_data["CoeffVHighStepArray_mV"] = np.linspace(Settings.json_data["CoeffStepMinVHigh_mV"], Settings.json_data["CoeffStepMaxVHigh_mV"], Settings.json_data["CoeffNumberOfVHighStep"])
            Settings.json_data["CoeffVHighStepArray_mV"] = [round(num, 0) for num in Settings.json_data["CoeffVHighStepArray_mV"]]
            Settings.json_data["CoeffStepMinCurrent_mA"] = int(CoeffStepMinCurrent_mA_value)
            Settings.json_data["CoeffStepMaxCurrent_mA"] = int(CoeffStepMaxCurrent_mA_value)
            Settings.json_data["CoeffNumberOfCurrentStep"] = int(CoeffNumberOfCurrentStep_value)
            Settings.json_data["CoeffCurrentStepArray_mA"] = np.linspace(Settings.json_data["CoeffStepMinCurrent_mA"], Settings.json_data["CoeffStepMaxCurrent_mA"], Settings.json_data["CoeffNumberOfCurrentStep"])
            Settings.json_data["CoeffCurrentStepArray_mA"] = [round(num, 0) for num in Settings.json_data["CoeffCurrentStepArray_mA"]]

            Settings.json_data["HistNumberOfPointsPerDuty"] = int(HistNumberOfPointsPerDuty_value)
            Settings.json_data["HistVHighCalibrationDutyPercent"] = int(HistVHighCalibrationDutyPercent_value)
            Settings.json_data["HistVHighCalibrationLowCurrent_mA"] = int(HistVHighCalibrationLowCurrent_mA_value)
            Settings.json_data["HistNumberOfVHighStep"] = int(HistNumberOfVHighStep_value)
            Settings.json_data["HistStepMinVHigh_mV"] = int(HistStepMinVHigh_mV_value)
            Settings.json_data["HistStepMaxVHigh_mV"] = int(HistStepMaxVHigh_mV_value)
            Settings.json_data["HistVHighStepArray_mV"] = np.linspace(Settings.json_data["HistStepMinVHigh_mV"], Settings.json_data["HistStepMaxVHigh_mV"], Settings.json_data["HistNumberOfVHighStep"])
            Settings.json_data["HistVHighStepArray_mV"] = [round(num, 0) for num in Settings.json_data["HistVHighStepArray_mV"]]
            
            # update the progress bar
            calcul_progress_bar_max_accuracy()
            calcul_progress_bar_max_coefficients()
            calcul_progress_bar_max_efficiency()
            calcul_progress_bar_max_histogram()
            
            # # communication of the new duty step
            # SPIN_Comm.UpdateDutyStep(int(duty_step_Percent_value))

            return "All parameters saved", "success"
    return "Save all parameters", "warning"



#####################################################################################
#                               Load existing parameters                            #
#####################################################################################

# creation of the InputGroup that allow the user to choose the parameters he wants from existing parameters
def load_existing_parameters():

    TestNamesOptions = []
    for testname in Settings.JsonTestsHistory_data["TestNamesHistory"]:
        TestNamesOptions.append({"label": testname, "value": testname})
    return(
                dbc.InputGroup([
                    dbc.InputGroupText("Name of the test from which you want to load the parameters"),
                    dbc.Select(
                        id="TestNamesLoadParameters",
                        options=TestNamesOptions,
                        value=None,
                        valid=False,
                        persistence_type='memory', 
                        persistence=True
                    )
                ])
            )

# callback that load exixting parameters from the input TestNamesLoadParameters chosen by the user
@callback(
    [
        dash.dependencies.Output("LoadInternalSafetyCurrent_A", "value"),   
        dash.dependencies.Output("LoadInternalSafetyPower_W", "value"),
        dash.dependencies.Output("NumberOfPointsPerDuty", "value"),
        dash.dependencies.Output("duty_step_Percent", "value"),
        dash.dependencies.Output("NumberOfStepInDutySweep", "value"),
        dash.dependencies.Output("starting_duty_cycle_Percent", "value"),
        dash.dependencies.Output("AccVHighCalibrationDutyPercent", "value"),
        dash.dependencies.Output("AccVHighCalibrationLowCurrent_mA", "value"),
        dash.dependencies.Output("AccIHighCalibrationDuty_Percent", "value"),
        dash.dependencies.Output("AccIHighCalibrationVHigh_mV", "value"),
        dash.dependencies.Output("AccVLowCalibrationLowCurrent_mA", "value"),
        dash.dependencies.Output("AccVLowCalibrationVHigh_mV", "value"),
        dash.dependencies.Output("AccILowCalibrationDuty_Percent", "value"),
        dash.dependencies.Output("AccILowCalibrationVHigh_mV", "value"),
        dash.dependencies.Output("AccNumberOfStepInVLowDutySweep", "value"),
        dash.dependencies.Output("AccNumberOfVHighStep", "value"),
        dash.dependencies.Output("AccStepMinVHigh_mV", "value"),
        dash.dependencies.Output("AccStepMaxVHigh_mV", "value"),
        dash.dependencies.Output("AccIHighNumberOfCurrentStep", "value"),
        dash.dependencies.Output("AccIHighStepMinCurrent_mA", "value"),
        dash.dependencies.Output("AccIHighStepMaxCurrent_mA", "value"),
        dash.dependencies.Output("AccILowNumberOfCurrentStep", "value"),
        dash.dependencies.Output("AccILowStepMinCurrent_mA", "value"),
        dash.dependencies.Output("AccILowStepMaxCurrent_mA", "value"),
        dash.dependencies.Output("EffNumberOfVHighStep", "value"),
        dash.dependencies.Output("EffStepMinVHigh_mV", "value"),
        dash.dependencies.Output("EffStepMaxVHigh_mV", "value"),
        dash.dependencies.Output("EffNumberOfIHighStep", "value"),
        dash.dependencies.Output("EffStepMinIHigh_mA", "value"),
        dash.dependencies.Output("EffStepMaxIHigh_mA", "value"),
        dash.dependencies.Output("CoeffNumberOfTWISTMeas", "value"),
        dash.dependencies.Output("CoeffVHighCalibrationDutyPercent", "value"),
        dash.dependencies.Output("CoeffVHighCalibrationLowCurrent_mA", "value"),
        dash.dependencies.Output("CoeffIHighCalibrationDuty_Percent", "value"),
        dash.dependencies.Output("CoeffIHighCalibrationVHigh_mV", "value"),
        dash.dependencies.Output("CoeffVLowCalibrationLowCurrent_mA", "value"),
        dash.dependencies.Output("CoeffVLowCalibrationVHigh_mV", "value"),
        dash.dependencies.Output("CoeffILowCalibrationDuty_Percent", "value"),
        dash.dependencies.Output("CoeffILowCalibrationVHigh_mV", "value"),
        dash.dependencies.Output("CoeffStepMinVHigh_mV", "value"),
        dash.dependencies.Output("CoeffStepMaxVHigh_mV", "value"),
        dash.dependencies.Output("CoeffNumberOfVHighStep", "value"),
        dash.dependencies.Output("CoeffStepMinCurrent_mA", "value"),
        dash.dependencies.Output("CoeffStepMaxCurrent_mA", "value"),
        dash.dependencies.Output("CoeffNumberOfCurrentStep", "value"),

        dash.dependencies.Output("HistNumberOfPointsPerDuty", "value"),
        dash.dependencies.Output("HistVHighCalibrationDutyPercent", "value"),
        dash.dependencies.Output("HistVHighCalibrationLowCurrent_mA", "value"),
        dash.dependencies.Output("HistNumberOfVHighStep", "value"),
        dash.dependencies.Output("HistStepMinVHigh_mV", "value"),
        dash.dependencies.Output("HistStepMaxVHigh_mV", "value"),

        Output("TestNamesLoadParameters", "valid"),
        Output("TestNamesLoadParameters", "invalid")
    ],
    [Input("TestNamesLoadParameters", "value")]
)
def load_parameters(TestNamesLoadParameters_value):
    if TestNamesLoadParameters_value is not None:
        if TestNamesLoadParameters_value is None:
            return Settings.NumberOfNoneArrayParamInJson * (None, ) + 2 * (False, ) + ("Valid")
        elif TestNamesLoadParameters_value in Settings.JsonTestsHistory_data["TestNamesHistory"]:
            if TestNamesLoadParameters_value == "DefaultParameters":
                with open("json_" + TestNamesLoadParameters_value + ".json",'r') as f:
                    body = json.load(f)
                    values_tup = tuple(body.values())
                return tuple(element for i, element in enumerate(values_tup) if i not in Settings.ArrayIndexInJson) + (True, False)
            else:
                DirJson = os.path.dirname(os.path.abspath(__file__))
                DirJson = os.path.dirname(DirJson)
                DirJson = os.path.join(DirJson, "Results")
                TestFolderPathJson = os.path.join(DirJson, TestNamesLoadParameters_value)
                JsonPath = TestFolderPathJson + "\json_" + TestNamesLoadParameters_value + ".json"
                with open(JsonPath,'r') as f:
                    body = json.load(f) # body is dict with json default parameters 
                    values_tup = tuple(body.values())
                return tuple(element for i, element in enumerate(values_tup) if i not in Settings.ArrayIndexInJson) + (True, False)
        else:
            return Settings.NumberOfNoneArrayParamInJson * (None, ) + (False, True)
    return Settings.NumberOfNoneArrayParamInJson * (None, ) + (False, False)



#####################################################################################
#                                 Coefficients Test                                 #
#####################################################################################

# creation of the coefficients test button
test_coefficients = dbc.Button(
                "Coefficients test", 
                id="test_coefficients_button",
                color="danger",
                n_clicks=0,
                ),

# creation of the card that contains the InputTexts to configure the coefficients test
Coefficients_Test_Parameters = dbc.Card(
            [
                dbc.CardHeader(
                    html.A(
                        "Coefficients test parameters",
                        id="coefficients_test_parameters_card_header",
                        className="coefficients_test_parameters_card_header",
                        style={"textDecoration": "none", "cursor": "pointer"},
                    )
                ),
                dbc.Collapse(
                    dbc.CardBody(
                        [
                        dbc.Button(html.I(className="fas fa-lightbulb", style={"margin_right": "4px"})
                                   , id="info_test_coefficients", outline=True, n_clicks=0),
                        dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("Information coefficients test")),
                            dbc.ModalBody(id="info_test_coefficients_modal_content"),
                            dbc.ModalFooter(
                                dbc.Button(
                                    "Close", id="info_test_coefficients_modal_close", className="ms_auto", n_clicks=0
                                )
                            ),
                        ],
                        id="info_test_coefficients_modal",
                        size="lg",
                        is_open=False,
                        ),
                        html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Number of samples read per duty (DMM and SPIN) for coefficients test"),
                                    dbc.Input(id="CoeffNumberOfTWISTMeas", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Duty cycle for the calibration of VHigh (percent)"),
                                    dbc.Input(id="CoeffVHighCalibrationDutyPercent", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Current drawn on low side for the calibration of VHigh (mA)"),
                                    dbc.Input(id="CoeffVHighCalibrationLowCurrent_mA", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Duty cycle for the calibration of IHigh (percent)"),
                                    dbc.Input(id="CoeffIHighCalibrationDuty_Percent", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("VHigh value for the calibration of IHigh (mV)"),
                                    dbc.Input(id="CoeffIHighCalibrationVHigh_mV", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Current drawn on low side for the calibration of VLow (mA)"),
                                    dbc.Input(id="CoeffVLowCalibrationLowCurrent_mA", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("VHigh value for the calibration of VLow (mV)"),
                                    dbc.Input(id="CoeffVLowCalibrationVHigh_mV", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Duty cycle for the calibration of ILow (percent)"),
                                    dbc.Input(id="CoeffILowCalibrationDuty_Percent", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("VHigh value for the calibration of ILow (mV)"),
                                    dbc.Input(id="CoeffILowCalibrationVHigh_mV", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Minimal value of VHigh for the VHigh calibration (mV)"),
                                    dbc.Input(id="CoeffStepMinVHigh_mV", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Maximal value of VHigh for the VHigh calibration (mV)"),
                                    dbc.Input(id="CoeffStepMaxVHigh_mV", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Number of VHigh steps for the VHigh calibration"),
                                    dbc.Input(id="CoeffNumberOfVHighStep", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.Button(
                                "Check",
                                id="check_CoeffVHighParametersForVHighCalibration_button",
                                color="warning"
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Minimal value of ILow for the ILow/IHigh calibration (mA)"),
                                    dbc.Input(id="CoeffStepMinCurrent_mA", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Maximal value of ILow for the ILow/IHigh calibration (mA)"),
                                    dbc.Input(id="CoeffStepMaxCurrent_mA", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Number of ILow steps for the VHigh calibration"),
                                    dbc.Input(id="CoeffNumberOfCurrentStep", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.Button(
                                "Check",
                                id="check_CoeffILowParametersForILowIHighCalibration_button",
                                color="warning"
                            ),
                        ]
                    ),
                    id="coefficients_test_parameters_card_collapse",
                ),
            ],
            id="coefficients_test_parameters_card", color = "", outline = True
        )

# callback that open/close the coefficients_test_parameters_card
@callback(
    Output("coefficients_test_parameters_card_collapse", "is_open"),
    [Input("coefficients_test_parameters_card_header", "n_clicks")],
    [dash.dependencies.State("coefficients_test_parameters_card_collapse", "is_open")],
)
def toggle_coefficients_test_parameters_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# callback that updates the coefficients_test_parameters_card color
@callback(
        Output("coefficients_test_parameters_card", "color"),
        Input("CoeffNumberOfTWISTMeas", "valid"),
        Input("CoeffVHighCalibrationDutyPercent", "valid"),
        Input("CoeffVHighCalibrationLowCurrent_mA", "valid"),
        Input("CoeffIHighCalibrationDuty_Percent", "valid"),
        Input("CoeffIHighCalibrationVHigh_mV", "valid"),
        Input("CoeffVLowCalibrationLowCurrent_mA", "valid"),
        Input("CoeffVLowCalibrationVHigh_mV", "valid"),
        Input("CoeffILowCalibrationDuty_Percent", "valid"),
        Input("CoeffILowCalibrationVHigh_mV", "valid"),
        Input("CoeffStepMinVHigh_mV", "valid"),
        Input("CoeffStepMaxVHigh_mV", "valid"),
        Input("CoeffNumberOfVHighStep", "valid"),
        Input("CoeffStepMinCurrent_mA", "valid"),
        Input("CoeffStepMaxCurrent_mA", "valid"),
        Input("CoeffNumberOfCurrentStep", "valid"),
        Input("CoeffNumberOfTWISTMeas", "invalid"),
        Input("CoeffVHighCalibrationDutyPercent", "invalid"),
        Input("CoeffVHighCalibrationLowCurrent_mA", "invalid"),
        Input("CoeffIHighCalibrationDuty_Percent", "invalid"),
        Input("CoeffIHighCalibrationVHigh_mV", "invalid"),
        Input("CoeffVLowCalibrationLowCurrent_mA", "invalid"),
        Input("CoeffVLowCalibrationVHigh_mV", "invalid"),
        Input("CoeffILowCalibrationDuty_Percent", "invalid"),
        Input("CoeffILowCalibrationVHigh_mV", "invalid"),
        Input("CoeffStepMinVHigh_mV", "invalid"),
        Input("CoeffStepMaxVHigh_mV", "invalid"),
        Input("CoeffNumberOfVHighStep", "invalid"),
        Input("CoeffStepMinCurrent_mA", "invalid"),
        Input("CoeffStepMaxCurrent_mA", "invalid"),
        Input("CoeffNumberOfCurrentStep", "invalid"),
        Input("CoeffNumberOfTWISTMeas", "value"),
        Input("CoeffVHighCalibrationDutyPercent", "value"),
        Input("CoeffVHighCalibrationLowCurrent_mA", "value"),
        Input("CoeffIHighCalibrationDuty_Percent", "value"),
        Input("CoeffIHighCalibrationVHigh_mV", "value"),
        Input("CoeffVLowCalibrationLowCurrent_mA", "value"),
        Input("CoeffVLowCalibrationVHigh_mV", "value"),
        Input("CoeffILowCalibrationDuty_Percent", "value"),
        Input("CoeffILowCalibrationVHigh_mV", "value"),
        Input("CoeffStepMinVHigh_mV", "value"),
        Input("CoeffStepMaxVHigh_mV", "value"),
        Input("CoeffNumberOfVHighStep", "value"),
        Input("CoeffStepMinCurrent_mA", "value"),
        Input("CoeffStepMaxCurrent_mA", "value"),
        Input("CoeffNumberOfCurrentStep", "value"),
        Input("TestNamesLoadParameters", "valid")
)
def update_coefficients_test_parameters_card_color(CoeffNumberOfTWISTMeas_validity, CoeffVHighCalibrationDutyPercent_validity, CoeffVHighCalibrationLowCurrent_mA_validity,
                                        CoeffIHighCalibrationDuty_Percent_validity, CoeffIHighCalibrationVHigh_mV_validity, CoeffVLowCalibrationLowCurrent_mA_validity,
                                        CoeffVLowCalibrationVHigh_mV_validity, CoeffILowCalibrationDuty_Percent_validity, CoeffILowCalibrationVHigh_mV_validity, 
                                        CoeffStepMinVHigh_mV_validity, CoeffStepMaxVHigh_mV_validity, CoeffNumberOfVHighStep_validity, CoeffStepMinCurrent_mA_validity, 
                                        CoeffStepMaxCurrent_mA_validity, CoeffNumberOfCurrentStep_validity, 
                                        CoeffNumberOfTWISTMeas_invalidity, CoeffVHighCalibrationDutyPercent_invalidity, CoeffVHighCalibrationLowCurrent_mA_invalidity,
                                        CoeffIHighCalibrationDuty_Percent_invalidity, CoeffIHighCalibrationVHigh_mV_invalidity, CoeffVLowCalibrationLowCurrent_mA_invalidity,
                                        CoeffVLowCalibrationVHigh_mV_invalidity, CoeffILowCalibrationDuty_Percent_invalidity, CoeffILowCalibrationVHigh_mV_invalidity, 
                                        CoeffStepMinVHigh_mV_invalidity, CoeffStepMaxVHigh_mV_invalidity, CoeffNumberOfVHighStep_invalidity, CoeffStepMinCurrent_mA_invalidity, 
                                        CoeffStepMaxCurrent_mA_invalidity, CoeffNumberOfCurrentStep_invalidity,
                                        CoeffNumberOfTWISTMeas_value, CoeffVHighCalibrationDutyPercent_value, CoeffVHighCalibrationLowCurrent_mA_value,
                                        CoeffIHighCalibrationDuty_Percent_value, CoeffIHighCalibrationVHigh_mV_value, CoeffVLowCalibrationLowCurrent_mA_value,
                                        CoeffVLowCalibrationVHigh_mV_value, CoeffILowCalibrationDuty_Percent_value, CoeffILowCalibrationVHigh_mV_value, 
                                        CoeffStepMinVHigh_mV_value, CoeffStepMaxVHigh_mV_value, CoeffNumberOfVHighStep_value, CoeffStepMinCurrent_mA_value, 
                                        CoeffStepMaxCurrent_mA_value, CoeffNumberOfCurrentStep_value,
                                        TestNamesLoadParameters_validity):
    if ((CoeffNumberOfTWISTMeas_validity and  CoeffVHighCalibrationDutyPercent_validity and CoeffVHighCalibrationLowCurrent_mA_validity and
                                        CoeffIHighCalibrationDuty_Percent_validity and CoeffIHighCalibrationVHigh_mV_validity and CoeffVLowCalibrationLowCurrent_mA_validity and
                                        CoeffVLowCalibrationVHigh_mV_validity and CoeffILowCalibrationDuty_Percent_validity and CoeffILowCalibrationVHigh_mV_validity and 
                                        CoeffStepMinVHigh_mV_validity and CoeffStepMaxVHigh_mV_validity and CoeffNumberOfVHighStep_validity and CoeffStepMinCurrent_mA_validity and 
                                        CoeffStepMaxCurrent_mA_validity and CoeffNumberOfCurrentStep_validity) or (TestNamesLoadParameters_validity and not (
                                        CoeffNumberOfTWISTMeas_invalidity or  CoeffVHighCalibrationDutyPercent_invalidity or CoeffVHighCalibrationLowCurrent_mA_invalidity or
                                        CoeffIHighCalibrationDuty_Percent_invalidity or CoeffIHighCalibrationVHigh_mV_invalidity or CoeffVLowCalibrationLowCurrent_mA_invalidity or
                                        CoeffVLowCalibrationVHigh_mV_invalidity or CoeffILowCalibrationDuty_Percent_invalidity or CoeffILowCalibrationVHigh_mV_invalidity or 
                                        CoeffStepMinVHigh_mV_invalidity or CoeffStepMaxVHigh_mV_invalidity or CoeffNumberOfVHighStep_invalidity or CoeffStepMinCurrent_mA_invalidity or 
                                        CoeffStepMaxCurrent_mA_invalidity or CoeffNumberOfCurrentStep_invalidity) and 
                                        CoeffNumberOfTWISTMeas_value !="" and  CoeffVHighCalibrationDutyPercent_value !="" and CoeffVHighCalibrationLowCurrent_mA_value !="" and
                                        CoeffIHighCalibrationDuty_Percent_value !="" and CoeffIHighCalibrationVHigh_mV_value !="" and CoeffVLowCalibrationLowCurrent_mA_value !="" and
                                        CoeffVLowCalibrationVHigh_mV_value !="" and CoeffILowCalibrationDuty_Percent_value !="" and CoeffILowCalibrationVHigh_mV_value !="" and 
                                        CoeffStepMinVHigh_mV_value !="" and CoeffStepMaxVHigh_mV_value !="" and CoeffNumberOfVHighStep_value !="" and CoeffStepMinCurrent_mA_value !="" and 
                                        CoeffStepMaxCurrent_mA_value !="" and CoeffNumberOfCurrentStep_value!="")):
        return "success"
    return ""

# callback that check the value of coefficients test parameters
@callback(
    Output("CoeffNumberOfTWISTMeas", "valid"),
    Output("CoeffNumberOfTWISTMeas", "invalid"),
    [Input("CoeffNumberOfTWISTMeas", "n_submit"), Input("CoeffNumberOfTWISTMeas", "n_blur")],
    State("CoeffNumberOfTWISTMeas", "value")
)
def check_CoeffNumberOfTWISTMeas_validity(CoeffNumberOfTWISTMeas_n_submit, CoeffNumberOfTWISTMeas_n_blur, CoeffNumberOfTWISTMeas_value):
    if CoeffNumberOfTWISTMeas_value and (CoeffNumberOfTWISTMeas_n_submit or CoeffNumberOfTWISTMeas_n_blur):
        if str(CoeffNumberOfTWISTMeas_value).isdigit() and int(CoeffNumberOfTWISTMeas_value) >= 1 and int(CoeffNumberOfTWISTMeas_value) <= 1000:
            return True, False
        return False, True
    return False, False

@callback(
    Output("CoeffVHighCalibrationDutyPercent", "valid"),
    Output("CoeffVHighCalibrationDutyPercent", "invalid"),
    [Input("CoeffVHighCalibrationDutyPercent", "n_submit"), Input("CoeffVHighCalibrationDutyPercent", "n_blur")],
    State("CoeffVHighCalibrationDutyPercent", "value"),
    State("starting_duty_cycle_Percent", "value")
)
def check_CoeffVHighCalibrationDutyPercent_validity(CoeffVHighCalibrationDutyPercent_n_submit, CoeffVHighCalibrationDutyPercent_n_blur, CoeffVHighCalibrationDutyPercent_value, starting_duty_cycle_Percent_value):
    if CoeffVHighCalibrationDutyPercent_value and starting_duty_cycle_Percent_value and (CoeffVHighCalibrationDutyPercent_n_submit or CoeffVHighCalibrationDutyPercent_n_blur):
        if str(CoeffVHighCalibrationDutyPercent_value).isdigit() and int(CoeffVHighCalibrationDutyPercent_value) >= int(starting_duty_cycle_Percent_value) and int(CoeffVHighCalibrationDutyPercent_value) <= 90:
            return True, False
        return False, True
    return False, False

@callback(
    Output("CoeffIHighCalibrationDuty_Percent", "valid"),
    Output("CoeffIHighCalibrationDuty_Percent", "invalid"),
    [Input("CoeffIHighCalibrationDuty_Percent", "n_submit"), Input("CoeffIHighCalibrationDuty_Percent", "n_blur")],
    State("CoeffIHighCalibrationDuty_Percent", "value"),
    State("starting_duty_cycle_Percent", "value")
)
def check_CoeffIHighCalibrationDuty_Percent_validity(CoeffIHighCalibrationDuty_Percent_n_submit, CoeffIHighCalibrationDuty_Percent_n_blur, CoeffIHighCalibrationDuty_Percent_value, starting_duty_cycle_Percent_value):
    if CoeffIHighCalibrationDuty_Percent_value and starting_duty_cycle_Percent_value and (CoeffIHighCalibrationDuty_Percent_n_submit or CoeffIHighCalibrationDuty_Percent_n_blur):
        if str(CoeffIHighCalibrationDuty_Percent_value).isdigit() and int(CoeffIHighCalibrationDuty_Percent_value) >= int(starting_duty_cycle_Percent_value) and int(CoeffIHighCalibrationDuty_Percent_value) <= 90:
            return True, False
        return False, True
    return False, False

@callback(
    Output("CoeffIHighCalibrationVHigh_mV", "valid"),
    Output("CoeffIHighCalibrationVHigh_mV", "invalid"),
    [Input("CoeffIHighCalibrationVHigh_mV", "n_submit"), Input("CoeffIHighCalibrationVHigh_mV", "n_blur")],
    State("CoeffIHighCalibrationVHigh_mV", "value")
)
def check_CoeffIHighCalibrationVHigh_mV_validity(CoeffIHighCalibrationVHigh_mV_n_submit, CoeffIHighCalibrationVHigh_mV_n_blur, CoeffIHighCalibrationVHigh_mV_value):
    if CoeffIHighCalibrationVHigh_mV_value and (CoeffIHighCalibrationVHigh_mV_n_submit or CoeffIHighCalibrationVHigh_mV_n_blur):
        if str(CoeffIHighCalibrationVHigh_mV_value).isdigit() and int(CoeffIHighCalibrationVHigh_mV_value) >= 10000 and int(CoeffIHighCalibrationVHigh_mV_value) <= 96000:
            return True, False
        return False, True
    return False, False

@callback(
    Output("CoeffVLowCalibrationLowCurrent_mA", "valid"),
    Output("CoeffVLowCalibrationLowCurrent_mA", "invalid"),
    [Input("CoeffVLowCalibrationLowCurrent_mA", "n_submit"), Input("CoeffVLowCalibrationLowCurrent_mA", "n_blur")],
    State("CoeffVLowCalibrationLowCurrent_mA", "value")
)
def check_CoeffVLowCalibrationLowCurrent_mA_validity(CoeffVLowCalibrationLowCurrent_mA_n_submit, CoeffVLowCalibrationLowCurrent_mA_n_blur, CoeffVLowCalibrationLowCurrent_mA_value):
    if CoeffVLowCalibrationLowCurrent_mA_value and (CoeffVLowCalibrationLowCurrent_mA_n_submit or CoeffVLowCalibrationLowCurrent_mA_n_blur):
        if str(CoeffVLowCalibrationLowCurrent_mA_value).isdigit() and int(CoeffVLowCalibrationLowCurrent_mA_value) >= 100 and int(CoeffVLowCalibrationLowCurrent_mA_value) <= 15000:
            return True, False
        return False, True
    return False, False

@callback(
    Output("CoeffVLowCalibrationVHigh_mV", "valid"),
    Output("CoeffVLowCalibrationVHigh_mV", "invalid"),
    [Input("CoeffVLowCalibrationVHigh_mV", "n_submit"), Input("CoeffVLowCalibrationVHigh_mV", "n_blur")],
    State("CoeffVLowCalibrationVHigh_mV", "value")
)
def check_CoeffVLowCalibrationVHigh_mV_validity(CoeffVLowCalibrationVHigh_mV_n_submit, CoeffVLowCalibrationVHigh_mV_n_blur, CoeffVLowCalibrationVHigh_mV_value):
    if CoeffVLowCalibrationVHigh_mV_value and (CoeffVLowCalibrationVHigh_mV_n_submit or CoeffVLowCalibrationVHigh_mV_n_blur):
        if str(CoeffVLowCalibrationVHigh_mV_value).isdigit() and int(CoeffVLowCalibrationVHigh_mV_value) >= 10000 and int(CoeffVLowCalibrationVHigh_mV_value) <= 96000:
            return True, False
        return False, True
    return False, False

@callback(
    Output("CoeffILowCalibrationDuty_Percent", "valid"),
    Output("CoeffILowCalibrationDuty_Percent", "invalid"),
    [Input("CoeffILowCalibrationDuty_Percent", "n_submit"), Input("CoeffILowCalibrationDuty_Percent", "n_blur")],
    State("CoeffILowCalibrationDuty_Percent", "value"),
    State("starting_duty_cycle_Percent", "value")
)
def check_CoeffILowCalibrationDuty_Percent_validity(CoeffILowCalibrationDuty_Percent_n_submit, CoeffILowCalibrationDuty_Percent_n_blur, CoeffILowCalibrationDuty_Percent_value, starting_duty_cycle_Percent_value):
    if CoeffILowCalibrationDuty_Percent_value and starting_duty_cycle_Percent_value and (CoeffILowCalibrationDuty_Percent_n_submit or CoeffILowCalibrationDuty_Percent_n_blur):
        if str(CoeffILowCalibrationDuty_Percent_value).isdigit() and int(CoeffILowCalibrationDuty_Percent_value) >= int(starting_duty_cycle_Percent_value) and int(CoeffILowCalibrationDuty_Percent_value) <= 90:
            return True, False
        return False, True
    return False, False

@callback(
    Output("CoeffILowCalibrationVHigh_mV", "valid"),
    Output("CoeffILowCalibrationVHigh_mV", "invalid"),
    [Input("CoeffILowCalibrationVHigh_mV", "n_submit"), Input("CoeffILowCalibrationVHigh_mV", "n_blur")],
    State("CoeffILowCalibrationVHigh_mV", "value")
)
def check_CoeffILowCalibrationVHigh_mV_validity(CoeffILowCalibrationVHigh_mV_n_submit, CoeffILowCalibrationVHigh_mV_n_blur, CoeffILowCalibrationVHigh_mV_value):
    if CoeffILowCalibrationVHigh_mV_value and (CoeffILowCalibrationVHigh_mV_n_submit or CoeffILowCalibrationVHigh_mV_n_blur):
        if str(CoeffILowCalibrationVHigh_mV_value).isdigit() and int(CoeffILowCalibrationVHigh_mV_value) >= 10000 and int(CoeffILowCalibrationVHigh_mV_value) <= 96000:
            return True, False
        return False, True
    return False, False

@callback(
    Output("CoeffVHighCalibrationLowCurrent_mA", "valid"),
    Output("CoeffVHighCalibrationLowCurrent_mA", "invalid"),
    [Input("CoeffVHighCalibrationLowCurrent_mA", "n_submit"), Input("CoeffVHighCalibrationLowCurrent_mA", "n_blur")],
    State("CoeffVHighCalibrationLowCurrent_mA", "value")
)
def check_CoeffVHighCalibrationLowCurrent_mA_validity(CoeffVHighCalibrationLowCurrent_mA_n_submit, CoeffVHighCalibrationLowCurrent_mA_n_blur, CoeffVHighCalibrationLowCurrent_mA_mV_value):
    if CoeffVHighCalibrationLowCurrent_mA_mV_value and (CoeffVHighCalibrationLowCurrent_mA_n_submit or CoeffVHighCalibrationLowCurrent_mA_n_blur):
        if str(CoeffVHighCalibrationLowCurrent_mA_mV_value).isdigit() and int(CoeffVHighCalibrationLowCurrent_mA_mV_value) >= 100 and int(CoeffVHighCalibrationLowCurrent_mA_mV_value) <= 15000:
            return True, False
        return False, True
    return False, False

@callback(
        Output("CoeffStepMinVHigh_mV", "valid"),
        Output("CoeffStepMinVHigh_mV", "invalid"),
        Output("CoeffStepMaxVHigh_mV", "valid"),
        Output("CoeffStepMaxVHigh_mV", "invalid"),
        Output("CoeffNumberOfVHighStep", "valid"),
        Output("CoeffNumberOfVHighStep", "invalid"),
        Output("check_CoeffVHighParametersForVHighCalibration_button", "color"),
        Output("check_CoeffVHighParametersForVHighCalibration_button", "children"),
        Input("check_CoeffVHighParametersForVHighCalibration_button", "n_clicks"),
        State("CoeffStepMinVHigh_mV", "value"),
        State("CoeffStepMaxVHigh_mV", "value"),
        State("CoeffNumberOfVHighStep", "value")
)
def check_CoeffVHighParametersForVHighCalibration(n, CoeffStepMinVHigh_mV_value, CoeffStepMaxVHigh_mV_value, CoeffNumberOfVHighStep_value):
    if n:
        if CoeffStepMinVHigh_mV_value is not None and CoeffStepMaxVHigh_mV_value is not None and CoeffNumberOfVHighStep_value is not None:
            if ((int(CoeffStepMaxVHigh_mV_value) > int(CoeffStepMinVHigh_mV_value) and int(CoeffNumberOfVHighStep_value) > 1) 
                or (int(CoeffStepMaxVHigh_mV_value) == int(CoeffStepMinVHigh_mV_value) and int(CoeffNumberOfVHighStep_value) == 1) 
                and (str(CoeffStepMinVHigh_mV_value).isdigit() and str(CoeffStepMaxVHigh_mV_value).isdigit() and str(CoeffNumberOfVHighStep_value).isdigit()
                     and int(CoeffStepMaxVHigh_mV_value)<=96000 and int(CoeffStepMinVHigh_mV_value)>=10000 and int(CoeffNumberOfVHighStep_value)<=1000)):
                return True, False, True, False, True, False, "success", "OK"
            return False, True, False, True, False, True, "danger", "Not OK"
        return False, True, False, True, False, True, "danger", "Not OK"
    return False, False, False, False, False, False, "warning", "Check"

@callback(
        Output("CoeffStepMinCurrent_mA", "valid"),
        Output("CoeffStepMinCurrent_mA", "invalid"),
        Output("CoeffStepMaxCurrent_mA", "valid"),
        Output("CoeffStepMaxCurrent_mA", "invalid"),
        Output("CoeffNumberOfCurrentStep", "valid"),
        Output("CoeffNumberOfCurrentStep", "invalid"),
        Output("check_CoeffILowParametersForILowIHighCalibration_button", "color"),
        Output("check_CoeffILowParametersForILowIHighCalibration_button", "children"),
        Input("check_CoeffILowParametersForILowIHighCalibration_button", "n_clicks"),
        State("CoeffStepMinCurrent_mA", "value"),
        State("CoeffStepMaxCurrent_mA", "value"),
        State("CoeffNumberOfCurrentStep", "value")
)
def check_CoeffILowParametersForILowIHighCalibration(n, CoeffStepMinCurrent_mA_value, CoeffStepMaxCurrent_mA_value, CoeffNumberOfCurrentStep_value):
    if n:
        if CoeffStepMinCurrent_mA_value is not None and CoeffStepMaxCurrent_mA_value is not None and CoeffNumberOfCurrentStep_value is not None:
            if ((int(CoeffStepMaxCurrent_mA_value) > int(CoeffStepMinCurrent_mA_value) and int(CoeffNumberOfCurrentStep_value) > 1) 
                or (int(CoeffStepMaxCurrent_mA_value) == int(CoeffStepMinCurrent_mA_value) and int(CoeffNumberOfCurrentStep_value) == 1) 
                and (str(CoeffStepMinCurrent_mA_value).isdigit() and str(CoeffStepMaxCurrent_mA_value).isdigit() and str(CoeffNumberOfCurrentStep_value).isdigit()
                     and int(CoeffStepMaxCurrent_mA_value)<=15000 and int(CoeffStepMinCurrent_mA_value)>=100 and int(CoeffNumberOfCurrentStep_value)<=1000)):
                return True, False, True, False, True, False, "success", "OK"
            return False, True, False, True, False, True, "danger", "Not OK"
        return False, True, False, True, False, True, "danger", "Not OK"
    return False, False, False, False, False, False, "warning", "Check"

# callback that open/close the modal that provides information concerning the test coefficients
@callback(
    Output("info_test_coefficients_modal", "is_open"),
    [Input("info_test_coefficients", "n_clicks"), Input("info_test_coefficients_modal_close", "n_clicks")],
    [State("info_test_coefficients_modal", "is_open")],
)
def toggle_info_test_coefficients_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# callback that display the content of the modal from the file markdown_test_info
@callback(
        Output("info_test_coefficients_modal_content", "children"),
        Input("info_test_coefficients", "n_clicks")
)
def display_info_test_coefficients_modal_content(n):
    if n:
        return dcc.Markdown(markdown_test_info.markdown_test_coefficients)

# creation of the progress bar maximale value for the coefficients test
def calcul_progress_bar_max_coefficients():
    global progress_bar_max_coefficients
    progress_bar_max_coefficients = Settings.CoeffNumberOfStepInDutySweep + 2*Settings.json_data["CoeffNumberOfCurrentStep"] + Settings.json_data["CoeffNumberOfVHighStep"] + len(Coefficients.CoeffDict.keys()) + 2
# initialization of the progress bar maximale value
calcul_progress_bar_max_coefficients()

# callback that launch coefficients test; update the test_coefficients_button and update the test information in the json (JsonTestsHistory_data)
@callback(   
    dash.dependencies.Output("test_coefficients_button", "children"),
    [dash.dependencies.Input("test_coefficients_button", "n_clicks")],
    [dash.dependencies.State("test_coefficients_button", "color"),
     dash.dependencies.State("TestName","value"),
     dash.dependencies.State("LowLeg","value"),
     dash.dependencies.State("BoardSN","value")
     ]
)
def launch_test_coefficients(n, test_coefficients_button, TestName, LowLeg, BoardSN):
    if TestName is None or LowLeg is None or BoardSN is None:
        raise PreventUpdate
    if n is None:
        raise PreventUpdate
    else:
        if test_coefficients_button == "success":  

            if "TestCoefficients" not in Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]:
                Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex].append("TestCoefficients")

            with open("JsonTestsHistory.json", "w") as f:
                json.dump(Settings.JsonTestsHistory_data, f, indent=4)

            Coefficients.GetCoefficients(TestName, BoardSN, int(LowLeg))
            return "Coefficients test Done"
        else:
            return "Coefficients test"



#####################################################################################
#                                  Efficiency Test                                  #
#####################################################################################

# creation of the efficiency test button
test_efficiency = dbc.Button(
                "Efficiency test", 
                id="test_efficiency_button",
                color="danger",
                n_clicks=0,
                ),

# creation of the card that contains the InputTexts to configure the efficiency test
Efficiency_Test_Parameters = dbc.Card(
        [
            dbc.CardHeader(
                html.A(
                    "Efficiency test parameters",
                    id="efficiency_test_parameters_card_header",
                    className="efficiency_test_parameters_card_header",
                    style={"textDecoration": "none", "cursor": "pointer"},
                )
            ),
            dbc.Collapse(
                dbc.CardBody(
                    [
                        dbc.Button(html.I(className="fas fa-lightbulb", style={"margin_right": "4px"}),
                                    id="info_test_efficiency", outline=True, n_clicks=0),
                        dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("Information efficiency test")),
                            dbc.ModalBody(id="info_test_efficiency_modal_content"),
                            dbc.ModalFooter(
                                dbc.Button(
                                    "Close", id="info_test_efficiency_modal_close", className="ms_auto", n_clicks=0
                                )
                            ),
                        ],
                        id="info_test_efficiency_modal",
                        size="lg",
                        is_open=False,
                        ),
                        html.Div(style={"height": "15px"}),
                        dbc.InputGroup([
                            dbc.InputGroupText("Number of times increasing the duty sweep for one IHigh value"),
                            dbc.Input(id="NumberOfStepInDutySweep", valid=False, invalid=False, persistence_type='memory', persistence=True)
                        ]),
                        html.Div(style={"height": "15px"}),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Number of VHigh steps"),
                                dbc.Input(id="EffNumberOfVHighStep", valid=False, invalid=False, persistence_type='memory', persistence=True),
                            ]
                        ),
                        dbc.InputGroup([
                            dbc.InputGroupText("Minimal value of VHigh (mV)"),
                            dbc.Input(id="EffStepMinVHigh_mV", valid=False, invalid=False, persistence_type='memory', persistence=True)
                        ]),
                        dbc.InputGroup([
                            dbc.InputGroupText("Maximal value of VHigh (mV)"),
                            dbc.Input(id="EffStepMaxVHigh_mV", valid=False, invalid=False, persistence_type='memory', persistence=True)
                        ]),
                        dbc.Button(
                            "Check",
                            id="check_EffVHighParameters_button",
                            color="success"
                        ),
                        html.Div(style={"height": "15px"}),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Number of IHigh steps"),
                                dbc.Input(id="EffNumberOfIHighStep", valid=False, invalid=False, persistence_type='memory', persistence=True),
                            ]
                        ),
                        dbc.InputGroup([
                            dbc.InputGroupText("Minimal value of IHigh (mA)"),
                            dbc.Input(id="EffStepMinIHigh_mA", valid=False, invalid=False, persistence_type='memory', persistence=True)
                        ]),
                        dbc.InputGroup([
                            dbc.InputGroupText("Maximal value of IHigh (mA)"),
                            dbc.Input(id="EffStepMaxIHigh_mA", valid=False, invalid=False, persistence_type='memory', persistence=True)
                        ]),
                        dbc.Button(
                            "Check",
                            id="check_EffIHighParameters_button",
                            color="success"
                        ),
                        html.Div(style={"height": "15px"}),
                    ],
                ),
                id="efficiency_test_parameters_card_collapse",
            ),
        ],
        id="efficiency_test_parameters_card", color = "", outline = True
    )

# callback that open/close the efficiency_test_parameters_card
@callback(
    Output("efficiency_test_parameters_card_collapse", "is_open"),
    [Input("efficiency_test_parameters_card_header", "n_clicks")],
    [dash.dependencies.State("efficiency_test_parameters_card_collapse", "is_open")],
)
def toggle_efficiency_test_parameters_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# callback that updates the efficiency_test_parameters_card color
@callback(
        Output("efficiency_test_parameters_card", "color"),
        Input("NumberOfStepInDutySweep", "valid"),
        Input("EffNumberOfVHighStep", "valid"),
        Input("EffStepMinVHigh_mV", "valid"),
        Input("EffStepMaxVHigh_mV", "valid"),
        Input("EffNumberOfIHighStep", "valid"),
        Input("EffStepMinIHigh_mA", "valid"),
        Input("EffStepMaxIHigh_mA", "valid"),
        Input("NumberOfStepInDutySweep", "invalid"),
        Input("EffNumberOfVHighStep", "invalid"),
        Input("EffStepMinVHigh_mV", "invalid"),
        Input("EffStepMaxVHigh_mV", "invalid"),
        Input("EffNumberOfIHighStep", "invalid"),
        Input("EffStepMinIHigh_mA", "invalid"),
        Input("EffStepMaxIHigh_mA", "invalid"),
        Input("NumberOfStepInDutySweep", "value"),
        Input("EffNumberOfVHighStep", "value"),
        Input("EffStepMinVHigh_mV", "value"),
        Input("EffStepMaxVHigh_mV", "value"),
        Input("EffNumberOfIHighStep", "value"),
        Input("EffStepMinIHigh_mA", "value"),
        Input("EffStepMaxIHigh_mA", "value"),
        Input("TestNamesLoadParameters", "valid")
)
def update_efficiency_test_parameters_card_color(NumberOfStepInDutySweep_validity, EffNumberOfVHighStep_validity, EffStepMinVHigh_mV_validity,
                                        EffStepMaxVHigh_mV_validity, EffNumberOfIHighStep_validity, EffStepMinIHigh_mA_validity,
                                        EffStepMaxIHigh_mA_validity,
                                        NumberOfStepInDutySweep_invalidity, EffNumberOfVHighStep_invalidity, EffStepMinVHigh_mV_invalidity,
                                        EffStepMaxVHigh_mV_invalidity, EffNumberOfIHighStep_invalidity, EffStepMinIHigh_mA_invalidity,
                                        EffStepMaxIHigh_mA_invalidity, 
                                        NumberOfStepInDutySweep_value, EffNumberOfVHighStep_value, EffStepMinVHigh_mV_value,
                                        EffStepMaxVHigh_mV_value, EffNumberOfIHighStep_value, EffStepMinIHigh_mA_value,
                                        EffStepMaxIHigh_mA_value, TestNamesLoadParameters_validity):
    if ((NumberOfStepInDutySweep_validity and EffNumberOfVHighStep_validity and EffStepMinVHigh_mV_validity and
                                        EffStepMaxVHigh_mV_validity and EffNumberOfIHighStep_validity and EffStepMinIHigh_mA_validity and
                                        EffStepMaxIHigh_mA_validity) or (TestNamesLoadParameters_validity and not (NumberOfStepInDutySweep_invalidity 
                                        or EffNumberOfVHighStep_invalidity or EffStepMinVHigh_mV_invalidity or
                                        EffStepMaxVHigh_mV_invalidity or EffNumberOfIHighStep_invalidity or EffStepMinIHigh_mA_invalidity or
                                        EffStepMaxIHigh_mA_invalidity) and NumberOfStepInDutySweep_value!="" and EffNumberOfVHighStep_value!="" and EffStepMinVHigh_mV_value!="" and
                                        EffStepMaxVHigh_mV_value!="" and EffNumberOfIHighStep_value!="" and EffStepMinIHigh_mA_value!="" and
                                        EffStepMaxIHigh_mA_value!="")):
        return "success"
    return ""

# callback that check the value of efficiency test parameters
@callback(
        Output("EffStepMinVHigh_mV", "valid"),
        Output("EffStepMinVHigh_mV", "invalid"),
        Output("EffStepMaxVHigh_mV", "valid"),
        Output("EffStepMaxVHigh_mV", "invalid"),
        Output("EffNumberOfVHighStep", "valid"),
        Output("EffNumberOfVHighStep", "invalid"),
        Output("check_EffVHighParameters_button", "color"),
        Output("check_EffVHighParameters_button", "children"),
        Input("check_EffVHighParameters_button", "n_clicks"),
        State("EffStepMinVHigh_mV", "value"),
        State("EffStepMaxVHigh_mV", "value"),
        State("EffNumberOfVHighStep", "value")
)
def check_EffVHighParameters(n, EffStepMinVHigh_mV_value, EffStepMaxVHigh_mV_value, EffNumberOfVHighStep_value):
    if n:
        if EffStepMinVHigh_mV_value is not None and EffStepMaxVHigh_mV_value is not None and EffNumberOfVHighStep_value is not None:
            if ((int(EffStepMaxVHigh_mV_value) > int(EffStepMinVHigh_mV_value) and int(EffNumberOfVHighStep_value) > 1) 
                or (int(EffStepMaxVHigh_mV_value) == int(EffStepMinVHigh_mV_value) and int(EffNumberOfVHighStep_value) == 1) 
                and (str(EffStepMinVHigh_mV_value).isdigit() and str(EffStepMaxVHigh_mV_value).isdigit() and str(EffNumberOfVHighStep_value).isdigit()
                     and int(EffStepMaxVHigh_mV_value)<=96000 and int(EffStepMinVHigh_mV_value)>=10000 and int(EffNumberOfVHighStep_value)<=1000)):
                return True, False, True, False, True, False, "success", "OK"
            return False, True, False, True, False, True, "danger", "Not OK"
        return False, True, False, True, False, True, "danger", "Not OK"
    return False, False, False, False, False, False, "warning", "Check"

@callback(
        Output("EffStepMinIHigh_mA", "valid"),
        Output("EffStepMinIHigh_mA", "invalid"),
        Output("EffStepMaxIHigh_mA", "valid"),
        Output("EffStepMaxIHigh_mA", "invalid"),
        Output("EffNumberOfIHighStep", "valid"),
        Output("EffNumberOfIHighStep", "invalid"),
        Output("check_EffIHighParameters_button", "color"),
        Output("check_EffIHighParameters_button", "children"),
        Input("check_EffIHighParameters_button", "n_clicks"),
        State("EffStepMinIHigh_mA", "value"),
        State("EffStepMaxIHigh_mA", "value"),
        State("EffNumberOfIHighStep", "value")
)
def check_EffIHighParameters(n, EffStepMinIHigh_mA_value, EffStepMaxIHigh_mA_value, EffNumberOfIHighStep_value):
    if n:
        if EffStepMinIHigh_mA_value is not None and EffStepMaxIHigh_mA_value is not None and EffNumberOfIHighStep_value is not None:
            if ((int(EffStepMaxIHigh_mA_value) > int(EffStepMinIHigh_mA_value) and int(EffNumberOfIHighStep_value) > 1) 
                or (int(EffStepMaxIHigh_mA_value) == int(EffStepMinIHigh_mA_value) and int(EffNumberOfIHighStep_value) == 1) 
                and (str(EffStepMinIHigh_mA_value).isdigit() and str(EffStepMaxIHigh_mA_value).isdigit() and str(EffNumberOfIHighStep_value).isdigit()
                     and int(EffStepMaxIHigh_mA_value)<=15000 and int(EffStepMinIHigh_mA_value)>=100 and int(EffNumberOfIHighStep_value)<=1000)):
                return True, False, True, False, True, False, "success", "OK"
            return False, True, False, True, False, True, "danger", "Not OK"
        return False, True, False, True, False, True, "danger", "Not OK"
    return False, False, False, False, False, False, "warning", "Check"

# callback that open/close the modal that provides information concerning the test efficiency
@callback(
    Output("info_test_efficiency_modal", "is_open"),
    [Input("info_test_efficiency", "n_clicks"), Input("info_test_efficiency_modal_close", "n_clicks")],
    [State("info_test_efficiency_modal", "is_open")],
)
def toggle_info_test_efficiency_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# callback that display the content of the modal from the file markdown_test_info
@callback(
        Output("info_test_efficiency_modal_content", "children"),
        Input("info_test_efficiency", "n_clicks")
)
def display_info_test_efficiency_modal_content(n):
    if n:
        return dcc.Markdown(markdown_test_info.markdown_test_efficiency)

# creation of the progress bar maximale value for the efficiency test
def calcul_progress_bar_max_efficiency():
    global progress_bar_max_efficiency
    progress_bar_max_efficiency = Settings.json_data["EffNumberOfVHighStep"]*Settings.json_data["EffNumberOfIHighStep"] + 2
# initialization of the progress bar maximale value
calcul_progress_bar_max_efficiency()

# callback that launch efficiency test; update the test_efficiency_button and update the test information in the json (JsonTestsHistory_data)
@callback(   
    dash.dependencies.Output("test_efficiency_button", "children"),
    [dash.dependencies.Input("test_efficiency_button", "n_clicks")],
    [dash.dependencies.State("test_efficiency_button", "color"),
     dash.dependencies.State("TestName","value"),
     dash.dependencies.State("LowLeg","value"),
     dash.dependencies.State("BoardSN","value")
     ]
)
def launch_test_efficiency(n, test_efficiency_button, TestName, LowLeg, BoardSN):
    if TestName is None or LowLeg is None or BoardSN is None and n is None:
        raise PreventUpdate
    else:
        if test_efficiency_button == "success":
            if "TestEfficiency" not in Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]:
                Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex].append("TestEfficiency")

            with open("JsonTestsHistory.json", "w") as f:
                json.dump(Settings.JsonTestsHistory_data, f, indent=4)

            LowLeg=int(LowLeg)
            Efficiency.MeasureEfficiency(TestName, LowLeg)
            return "Efficiency test Done"
        else:
            return "Efficiency test"



#####################################################################################
#                                   Accuracy Test                                   #
#####################################################################################

# creation of the accuracy test button
test_accuracy = dbc.Button(
                "Accuracy test", 
                id="test_accuracy_button",
                color="danger",
                n_clicks=0,
                ),

# creation of the card that contains the InputTexts to configure the accuracy test
Accuracy_Test_Parameters = dbc.Card(
            [
                dbc.CardHeader(
                    html.A(
                        "Accuracy test parameters",
                        id="accuracy_test_parameters_card_header",
                        className="accuracy_test_parameters_card_header",
                        style={"textDecoration": "none", "cursor": "pointer"},
                    )
                ),
                dbc.Collapse(
                    dbc.CardBody(
                        [
                        dbc.Button(html.I(className="fas fa-lightbulb", style={"margin_right": "4px"}),
                                    id="info_test_accuracy", outline=True, n_clicks=0),
                        dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("Information accuracy test")),
                            dbc.ModalBody(id="info_test_accuracy_modal_content"),
                            dbc.ModalFooter(
                                dbc.Button(
                                    "Close", id="info_test_accuracy_modal_close", className="ms_auto", n_clicks=0
                                )
                            ),
                        ],
                        id="info_test_accuracy_modal",
                        size="lg",
                        is_open=False,
                        ),
                        html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Duty cycle for the VHigh measures (percent)"),
                                    dbc.Input(id="AccVHighCalibrationDutyPercent", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Current sink by the load for the VHigh measures (mA)"),
                                    dbc.Input(id="AccVHighCalibrationLowCurrent_mA", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Duty cycle value for the IHigh measures (percent)"),
                                    dbc.Input(id="AccIHighCalibrationDuty_Percent", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("VHigh value for the IHigh measures (mV)"),
                                    dbc.Input(id="AccIHighCalibrationVHigh_mV", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Current sink by the load for the VLow measures (mA)"),
                                    dbc.Input(id="AccVLowCalibrationLowCurrent_mA", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("VHigh value for the VLow measures (mV)"),
                                    dbc.Input(id="AccVLowCalibrationVHigh_mV", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Duty cycle value for the ILow measures (percent)"),
                                    dbc.Input(id="AccILowCalibrationDuty_Percent", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("VHigh value for the ILow measures (mV)"),
                                    dbc.Input(id="AccILowCalibrationVHigh_mV", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Number of steps for VLow measures"),
                                    dbc.Input(id="AccNumberOfStepInVLowDutySweep", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Number of VHigh steps for VHigh measures"),
                                    dbc.Input(id="AccNumberOfVHighStep", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Value of the first VHigh step for VHigh measures (mV)"),
                                    dbc.Input(id="AccStepMinVHigh_mV", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Value of the last VHigh step for VHigh measures (mV)"),
                                    dbc.Input(id="AccStepMaxVHigh_mV", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.Button(
                                "Check",
                                id="check_AccVHighParameters_button",
                                color="warning"
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Number of IHigh steps for IHigh measures"),
                                    dbc.Input(id="AccIHighNumberOfCurrentStep", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Value of the first IHigh step for IHigh measures (mA)"),
                                    dbc.Input(id="AccIHighStepMinCurrent_mA", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Value of the last IHigh step for IHigh measures (mA)"),
                                    dbc.Input(id="AccIHighStepMaxCurrent_mA", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.Button(
                                "Check",
                                id="check_AccIHighParameters_button",
                                color="warning"
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Number of ILow steps for ILow measures"),
                                    dbc.Input(id="AccILowNumberOfCurrentStep", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Value of the first ILow step for ILow measures (mA)"),
                                    dbc.Input(id="AccILowStepMinCurrent_mA", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Value of the last ILow step for ILow measures (mA)"),
                                    dbc.Input(id="AccILowStepMaxCurrent_mA", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.Button(
                                "Check",
                                id="check_AccILowParameters_button",
                                color="warning"
                            ),
                            html.Div(style={"height": "15px"}),
                        ]
                    ),
                    id="accuracy_test_parameters_card_collapse",
                ),
            ],
        id="accuracy_test_parameters_card", color = "", outline = True
        )

# callback that open/close the accuracy_test_parameters_card
@callback(
    Output("accuracy_test_parameters_card_collapse", "is_open"),
    [Input("accuracy_test_parameters_card_header", "n_clicks")],
    dash.dependencies.State("accuracy_test_parameters_card_collapse", "is_open")
)
def toggle_accuracy_test_parameters_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# callback that updates the accuracy_test_parameters_card color
@callback(
        Output("accuracy_test_parameters_card", "color"),
        Input("AccVHighCalibrationDutyPercent", "valid"),
        Input("AccVHighCalibrationLowCurrent_mA", "valid"),
        Input("AccIHighCalibrationDuty_Percent", "valid"),
        Input("AccIHighCalibrationVHigh_mV", "valid"),
        Input("AccVLowCalibrationLowCurrent_mA", "valid"),
        Input("AccVLowCalibrationVHigh_mV", "valid"),
        Input("AccILowCalibrationDuty_Percent", "valid"),
        Input("AccILowCalibrationVHigh_mV", "valid"),
        Input("AccNumberOfStepInVLowDutySweep", "valid"),
        Input("AccNumberOfVHighStep", "valid"),
        Input("AccStepMinVHigh_mV", "valid"),
        Input("AccStepMaxVHigh_mV", "valid"),
        Input("AccIHighNumberOfCurrentStep", "valid"),
        Input("AccIHighStepMinCurrent_mA", "valid"),
        Input("AccIHighStepMaxCurrent_mA", "valid"),
        Input("AccILowNumberOfCurrentStep", "valid"),
        Input("AccILowStepMinCurrent_mA", "valid"),
        Input("AccILowStepMaxCurrent_mA", "valid"),
        Input("AccVHighCalibrationDutyPercent", "invalid"),
        Input("AccVHighCalibrationLowCurrent_mA", "invalid"),
        Input("AccIHighCalibrationDuty_Percent", "invalid"),
        Input("AccIHighCalibrationVHigh_mV", "invalid"),
        Input("AccVLowCalibrationLowCurrent_mA", "invalid"),
        Input("AccVLowCalibrationVHigh_mV", "invalid"),
        Input("AccILowCalibrationDuty_Percent", "invalid"),
        Input("AccILowCalibrationVHigh_mV", "invalid"),
        Input("AccNumberOfStepInVLowDutySweep", "invalid"),
        Input("AccNumberOfVHighStep", "invalid"),
        Input("AccStepMinVHigh_mV", "invalid"),
        Input("AccStepMaxVHigh_mV", "invalid"),
        Input("AccIHighNumberOfCurrentStep", "invalid"),
        Input("AccIHighStepMinCurrent_mA", "invalid"),
        Input("AccIHighStepMaxCurrent_mA", "invalid"),
        Input("AccILowNumberOfCurrentStep", "invalid"),
        Input("AccILowStepMinCurrent_mA", "invalid"),
        Input("AccILowStepMaxCurrent_mA", "invalid"),
        Input("AccVHighCalibrationDutyPercent", "value"),
        Input("AccVHighCalibrationLowCurrent_mA", "value"),
        Input("AccIHighCalibrationDuty_Percent", "value"),
        Input("AccIHighCalibrationVHigh_mV", "value"),
        Input("AccVLowCalibrationLowCurrent_mA", "value"),
        Input("AccVLowCalibrationVHigh_mV", "value"),
        Input("AccILowCalibrationDuty_Percent", "value"),
        Input("AccILowCalibrationVHigh_mV", "value"),
        Input("AccNumberOfStepInVLowDutySweep", "value"),
        Input("AccNumberOfVHighStep", "value"),
        Input("AccStepMinVHigh_mV", "value"),
        Input("AccStepMaxVHigh_mV", "value"),
        Input("AccIHighNumberOfCurrentStep", "value"),
        Input("AccIHighStepMinCurrent_mA", "value"),
        Input("AccIHighStepMaxCurrent_mA", "value"),
        Input("AccILowNumberOfCurrentStep", "value"),
        Input("AccILowStepMinCurrent_mA", "value"),
        Input("AccILowStepMaxCurrent_mA", "value"),
        Input("TestNamesLoadParameters", "valid")
)
def update_accuracy_test_parameters_card_color(AccVHighCalibrationDutyPercent_validity, AccVHighCalibrationLowCurrent_mA_validity, AccIHighCalibrationDuty_Percent_validity, AccIHighCalibrationVHigh_mV_validity,
     AccVLowCalibrationLowCurrent_mA_validity, AccVLowCalibrationVHigh_mV_validity, AccILowCalibrationDuty_Percent_validity, AccILowCalibrationVHigh_mV_validity,
     AccNumberOfStepInVLowDutySweep_validity, AccNumberOfVHighStep_validity, AccStepMinVHigh_mV_validity, AccStepMaxVHigh_mV_validity, AccIHighNumberOfCurrentStep_validity,
     AccIHighStepMinCurrent_mA_validity, AccIHighStepMaxCurrent_mA_validity, AccILowNumberOfCurrentStep_validity, AccILowStepMinCurrent_mA_validity,
     AccILowStepMaxCurrent_mA_validity, AccVHighCalibrationDutyPercent_invalidity, AccVHighCalibrationLowCurrent_mA_invalidity, AccIHighCalibrationDuty_Percent_invalidity, AccIHighCalibrationVHigh_mV_invalidity,
     AccVLowCalibrationLowCurrent_mA_invalidity, AccVLowCalibrationVHigh_mV_invalidity, AccILowCalibrationDuty_Percent_invalidity, AccILowCalibrationVHigh_mV_invalidity,
     AccNumberOfStepInVLowDutySweep_invalidity, AccNumberOfVHighStep_invalidity, AccStepMinVHigh_mV_invalidity, AccStepMaxVHigh_mV_invalidity, AccIHighNumberOfCurrentStep_invalidity,
     AccIHighStepMinCurrent_mA_invalidity, AccIHighStepMaxCurrent_mA_invalidity, AccILowNumberOfCurrentStep_invalidity, AccILowStepMinCurrent_mA_invalidity,
     AccILowStepMaxCurrent_mA_invalidity, 
     AccVHighCalibrationDutyPercent_value, AccVHighCalibrationLowCurrent_mA_value, AccIHighCalibrationDuty_Percent_value, AccIHighCalibrationVHigh_mV_value,
     AccVLowCalibrationLowCurrent_mA_value, AccVLowCalibrationVHigh_mV_value, AccILowCalibrationDuty_Percent_value, AccILowCalibrationVHigh_mV_value,
     AccNumberOfStepInVLowDutySweep_value, AccNumberOfVHighStep_value, AccStepMinVHigh_mV_value, AccStepMaxVHigh_mV_value, AccIHighNumberOfCurrentStep_value,
     AccIHighStepMinCurrent_mA_value, AccIHighStepMaxCurrent_mA_value, AccILowNumberOfCurrentStep_value, AccILowStepMinCurrent_mA_value,
     AccILowStepMaxCurrent_mA_value,     
     TestNamesLoadParameters_validity):
    if ((AccVHighCalibrationDutyPercent_validity and AccVHighCalibrationLowCurrent_mA_validity and AccIHighCalibrationDuty_Percent_validity and AccIHighCalibrationVHigh_mV_validity and
        AccVLowCalibrationLowCurrent_mA_validity and AccVLowCalibrationVHigh_mV_validity and AccILowCalibrationDuty_Percent_validity and AccILowCalibrationVHigh_mV_validity and
        AccNumberOfStepInVLowDutySweep_validity and AccNumberOfVHighStep_validity and AccStepMinVHigh_mV_validity and AccStepMaxVHigh_mV_validity and AccIHighNumberOfCurrentStep_validity and
        AccIHighStepMinCurrent_mA_validity and AccIHighStepMaxCurrent_mA_validity and AccILowNumberOfCurrentStep_validity and AccILowStepMinCurrent_mA_validity and
        AccILowStepMaxCurrent_mA_validity) or (TestNamesLoadParameters_validity and not (AccVHighCalibrationDutyPercent_invalidity or AccVHighCalibrationLowCurrent_mA_invalidity or AccIHighCalibrationDuty_Percent_invalidity or AccIHighCalibrationVHigh_mV_invalidity or
        AccVLowCalibrationLowCurrent_mA_invalidity or AccVLowCalibrationVHigh_mV_invalidity or AccILowCalibrationDuty_Percent_invalidity or AccILowCalibrationVHigh_mV_invalidity or
        AccNumberOfStepInVLowDutySweep_invalidity or AccNumberOfVHighStep_invalidity or AccStepMinVHigh_mV_invalidity or AccStepMaxVHigh_mV_invalidity or AccIHighNumberOfCurrentStep_invalidity or
        AccIHighStepMinCurrent_mA_invalidity or AccIHighStepMaxCurrent_mA_invalidity or AccILowNumberOfCurrentStep_invalidity or AccILowStepMinCurrent_mA_invalidity or
        AccILowStepMaxCurrent_mA_invalidity) and AccVHighCalibrationDutyPercent_value!="" and AccVHighCalibrationLowCurrent_mA_value!="" and AccIHighCalibrationDuty_Percent_value!="" and AccIHighCalibrationVHigh_mV_value!="" and
     AccVLowCalibrationLowCurrent_mA_value!="" and AccVLowCalibrationVHigh_mV_value!="" and AccILowCalibrationDuty_Percent_value!="" and AccILowCalibrationVHigh_mV_value!="" and
     AccNumberOfStepInVLowDutySweep_value!="" and AccNumberOfVHighStep_value!="" and AccStepMinVHigh_mV_value!="" and AccStepMaxVHigh_mV_value!="" and AccIHighNumberOfCurrentStep_value!="" and
     AccIHighStepMinCurrent_mA_value!="" and AccIHighStepMaxCurrent_mA_value!="" and AccILowNumberOfCurrentStep_value!="" and AccILowStepMinCurrent_mA_value!="" and
     AccILowStepMaxCurrent_mA_value!="")):
        return "success"
    return ""

# callback that check the value of accuracy test parameters
@callback(
    Output("AccVHighCalibrationDutyPercent", "valid"),
    Output("AccVHighCalibrationDutyPercent", "invalid"),
    [Input("AccVHighCalibrationDutyPercent", "n_submit"), Input("AccVHighCalibrationDutyPercent", "n_blur")],
    State("AccVHighCalibrationDutyPercent", "value"),
    State("starting_duty_cycle_Percent", "value")
)
def check_AccVHighCalibrationDutyPercent_validity(AccVHighCalibrationDutyPercent_n_submit, AccVHighCalibrationDutyPercent_n_bur, AccVHighCalibrationDutyPercent_value, starting_duty_cycle_Percent_value):
    if AccVHighCalibrationDutyPercent_value and starting_duty_cycle_Percent_value and (AccVHighCalibrationDutyPercent_n_submit or AccVHighCalibrationDutyPercent_n_bur):
        if str(AccVHighCalibrationDutyPercent_value).isdigit() and int(AccVHighCalibrationDutyPercent_value) >= int(starting_duty_cycle_Percent_value) and int(AccVHighCalibrationDutyPercent_value) <= 90:
            return True, False
        return False, True
    return False, False

@callback(
    Output("AccIHighCalibrationDuty_Percent", "valid"),
    Output("AccIHighCalibrationDuty_Percent", "invalid"),
    [Input("AccIHighCalibrationDuty_Percent", "n_submit"), Input("AccIHighCalibrationDuty_Percent", "n_blur")],
    State("AccIHighCalibrationDuty_Percent", "value"),
    State("starting_duty_cycle_Percent", "value")
)
def check_AccIHighCalibrationDuty_Percent_validity(AccIHighCalibrationDuty_Percent_n_submit, AccIHighCalibrationDuty_Percent_n_bur, AccIHighCalibrationDuty_Percent_value, starting_duty_cycle_Percent_value):
    if AccIHighCalibrationDuty_Percent_value and starting_duty_cycle_Percent_value and (AccIHighCalibrationDuty_Percent_n_submit or AccIHighCalibrationDuty_Percent_n_bur):
        if str(AccIHighCalibrationDuty_Percent_value).isdigit() and int(AccIHighCalibrationDuty_Percent_value) >= int(starting_duty_cycle_Percent_value) and int(AccIHighCalibrationDuty_Percent_value) <= 90:
            return True, False
        return False, True
    return False, False

@callback(
    Output("AccVHighCalibrationLowCurrent_mA", "valid"),
    Output("AccVHighCalibrationLowCurrent_mA", "invalid"),
    [Input("AccVHighCalibrationLowCurrent_mA", "n_submit"), Input("AccVHighCalibrationLowCurrent_mA", "n_blur")],
    State("AccVHighCalibrationLowCurrent_mA", "value")
)
def check_AccVHighCalibrationLowCurrent_mA_validity(AccVHighCalibrationLowCurrent_mA_n_submit, AccVHighCalibrationLowCurrent_mA_n_bur, AccVHighCalibrationLowCurrent_mA_value):
    if AccVHighCalibrationLowCurrent_mA_value and (AccVHighCalibrationLowCurrent_mA_n_submit or AccVHighCalibrationLowCurrent_mA_n_bur):
        if str(AccVHighCalibrationLowCurrent_mA_value).isdigit() and int(AccVHighCalibrationLowCurrent_mA_value) >= 100 and int(AccVHighCalibrationLowCurrent_mA_value) <= 15000:
            return True, False
        return False, True
    return False, False

@callback(
    Output("AccVLowCalibrationLowCurrent_mA", "valid"),
    Output("AccVLowCalibrationLowCurrent_mA", "invalid"),
    [Input("AccVLowCalibrationLowCurrent_mA", "n_submit"), Input("AccVLowCalibrationLowCurrent_mA", "n_blur")],
    State("AccVLowCalibrationLowCurrent_mA", "value")
)
def check_AccVLowCalibrationLowCurrent_mA_validity(AccVLowCalibrationLowCurrent_mA_n_submit, AccVLowCalibrationLowCurrent_mA_n_bur, AccVLowCalibrationLowCurrent_mA_mA_value):
    if AccVLowCalibrationLowCurrent_mA_mA_value and (AccVLowCalibrationLowCurrent_mA_n_submit or AccVLowCalibrationLowCurrent_mA_n_bur):
        if str(AccVLowCalibrationLowCurrent_mA_mA_value).isdigit() and int(AccVLowCalibrationLowCurrent_mA_mA_value) >= 100 and int(AccVLowCalibrationLowCurrent_mA_mA_value) <= 15000:
            return True, False
        return False, True
    return False, False 

@callback(
    Output("AccIHighCalibrationVHigh_mV", "valid"),
    Output("AccIHighCalibrationVHigh_mV", "invalid"),
    [Input("AccIHighCalibrationVHigh_mV", "n_submit"), Input("AccIHighCalibrationVHigh_mV", "n_blur")],
    State("AccIHighCalibrationVHigh_mV", "value")
)
def check_AccIHighCalibrationVHigh_mV_validity(AccIHighCalibrationVHigh_mV_n_submit, AccIHighCalibrationVHigh_mV_n_blur, AccIHighCalibrationVHigh_mV_value):
    if AccIHighCalibrationVHigh_mV_value and (AccIHighCalibrationVHigh_mV_n_submit or AccIHighCalibrationVHigh_mV_n_blur):
        if str(AccIHighCalibrationVHigh_mV_value).isdigit() and int(AccIHighCalibrationVHigh_mV_value) >= 10000 and int(AccIHighCalibrationVHigh_mV_value) <= 96000:
            return True, False
        return False, True
    return False, False

@callback(
    Output("AccVLowCalibrationVHigh_mV", "valid"),
    Output("AccVLowCalibrationVHigh_mV", "invalid"),
    [Input("AccVLowCalibrationVHigh_mV", "n_submit"), Input("AccVLowCalibrationVHigh_mV", "n_blur")],
    State("AccVLowCalibrationVHigh_mV", "value")
)
def check_AccVLowCalibrationVHigh_mV_validity(AccVLowCalibrationVHigh_mV_n_submit, AccVLowCalibrationVHigh_mV_n_blur, AccVLowCalibrationVHigh_mV_value):
    if AccVLowCalibrationVHigh_mV_value and (AccVLowCalibrationVHigh_mV_n_submit or AccVLowCalibrationVHigh_mV_n_blur):
        if str(AccVLowCalibrationVHigh_mV_value).isdigit() and int(AccVLowCalibrationVHigh_mV_value) >= 10000 and int(AccVLowCalibrationVHigh_mV_value) <= 96000:
            return True, False
        return False, True
    return False, False

@callback(
    Output("AccILowCalibrationDuty_Percent", "valid"),
    Output("AccILowCalibrationDuty_Percent", "invalid"),
    [Input("AccILowCalibrationDuty_Percent", "n_submit"), Input("AccILowCalibrationDuty_Percent", "n_blur")],
    State("AccILowCalibrationDuty_Percent", "value"),
    State("starting_duty_cycle_Percent", "value")
)
def check_AccILowCalibrationDuty_Percent_validity(AccILowCalibrationDuty_Percent_n_submit, AccILowCalibrationDuty_Percent_n_blur, AccILowCalibrationDuty_Percent_value, starting_duty_cycle_Percent_value):
    if AccILowCalibrationDuty_Percent_value and starting_duty_cycle_Percent_value and (AccILowCalibrationDuty_Percent_n_submit or AccILowCalibrationDuty_Percent_n_blur):
        if str(AccILowCalibrationDuty_Percent_value).isdigit() and int(AccILowCalibrationDuty_Percent_value) >= int(starting_duty_cycle_Percent_value) and int(AccILowCalibrationDuty_Percent_value) <= 90:
            return True, False
        return False, True
    return False, False

@callback(
    Output("AccILowCalibrationVHigh_mV", "valid"),
    Output("AccILowCalibrationVHigh_mV", "invalid"),
    [Input("AccILowCalibrationVHigh_mV", "n_submit"), Input("AccILowCalibrationVHigh_mV", "n_blur")],
    State("AccILowCalibrationVHigh_mV", "value")
)
def check_AccILowCalibrationVHigh_mV_validity(AccILowCalibrationVHigh_mV_n_submit, AccILowCalibrationVHigh_mV_n_blur, AccILowCalibrationVHigh_mV_value):
    if AccILowCalibrationVHigh_mV_value and (AccILowCalibrationVHigh_mV_n_submit or AccILowCalibrationVHigh_mV_n_blur):
        if str(AccILowCalibrationVHigh_mV_value).isdigit() and int(AccILowCalibrationVHigh_mV_value) >= 10000 and int(AccILowCalibrationVHigh_mV_value) <= 96000:
            return True, False
        return False, True
    return False, False

@callback(
    Output("AccNumberOfStepInVLowDutySweep", "valid"),
    Output("AccNumberOfStepInVLowDutySweep", "invalid"),
    [Input("AccNumberOfStepInVLowDutySweep", "n_submit"), Input("AccNumberOfStepInVLowDutySweep", "n_blur")],
    State("AccNumberOfStepInVLowDutySweep", "value")
)
def check_AccNumberOfStepInVLowDutySweep_validity(AccNumberOfStepInVLowDutySweep_n_submit, AccNumberOfStepInVLowDutySweep_n_blur, AccNumberOfStepInVLowDutySweep_value):
    if AccNumberOfStepInVLowDutySweep_value and (AccNumberOfStepInVLowDutySweep_n_submit or AccNumberOfStepInVLowDutySweep_n_blur):
        if str(AccNumberOfStepInVLowDutySweep_value).isdigit() and int(AccNumberOfStepInVLowDutySweep_value) >= 1 and int(AccNumberOfStepInVLowDutySweep_value) <= 1000:
            return True, False
        return False, True
    return False, False

@callback(
        Output("AccStepMinVHigh_mV", "valid"),
        Output("AccStepMinVHigh_mV", "invalid"),
        Output("AccStepMaxVHigh_mV", "valid"),
        Output("AccStepMaxVHigh_mV", "invalid"),
        Output("AccNumberOfVHighStep", "valid"),
        Output("AccNumberOfVHighStep", "invalid"),
        Output("check_AccVHighParameters_button", "color"),
        Output("check_AccVHighParameters_button", "children"),
        Input("check_AccVHighParameters_button", "n_clicks"),
        State("AccStepMinVHigh_mV", "value"),
        State("AccStepMaxVHigh_mV", "value"),
        State("AccNumberOfVHighStep", "value")
)
def check_AccVHighParameters(n, AccStepMinVHigh_mV_value, AccStepMaxVHigh_mV_value, AccNumberOfVHighStep_value):
    if n:
        if AccStepMinVHigh_mV_value is not None and AccStepMaxVHigh_mV_value is not None and AccNumberOfVHighStep_value is not None:
            if ((int(AccStepMaxVHigh_mV_value) > int(AccStepMinVHigh_mV_value) and int(AccNumberOfVHighStep_value) > 1) 
                or (int(AccStepMaxVHigh_mV_value) == int(AccStepMinVHigh_mV_value) and int(AccNumberOfVHighStep_value) == 1) 
                and (str(AccStepMinVHigh_mV_value).isdigit() and str(AccStepMaxVHigh_mV_value).isdigit() and str(AccNumberOfVHighStep_value).isdigit()
                     and int(AccStepMaxVHigh_mV_value)<=96000 and int(AccStepMinVHigh_mV_value)>=10000 and int(AccNumberOfVHighStep_value)<=1000)):
                return True, False, True, False, True, False, "success", "OK"
            return False, True, False, True, False, True, "danger", "Not OK"
        return False, True, False, True, False, True, "danger", "Not OK"
    return False, False, False, False, False, False, "warning", "Check"

@callback(
        Output("AccIHighStepMinCurrent_mA", "valid"),
        Output("AccIHighStepMinCurrent_mA", "invalid"),
        Output("AccIHighStepMaxCurrent_mA", "valid"),
        Output("AccIHighStepMaxCurrent_mA", "invalid"),
        Output("AccIHighNumberOfCurrentStep", "valid"),
        Output("AccIHighNumberOfCurrentStep", "invalid"),
        Output("check_AccIHighParameters_button", "color"),
        Output("check_AccIHighParameters_button", "children"),
        Input("check_AccIHighParameters_button", "n_clicks"),
        State("AccIHighStepMinCurrent_mA", "value"),
        State("AccIHighStepMaxCurrent_mA", "value"),
        State("AccIHighNumberOfCurrentStep", "value")
)
def check_AccIHighParameters(n, AccIHighStepMinCurrent_mA_value, AccIHighStepMaxCurrent_mA_value, AccIHighNumberOfCurrentStep_value):
    if n:
        if AccIHighStepMinCurrent_mA_value is not None and AccIHighStepMaxCurrent_mA_value is not None and AccIHighNumberOfCurrentStep_value is not None:
            if ((int(AccIHighStepMaxCurrent_mA_value) > int(AccIHighStepMinCurrent_mA_value) and int(AccIHighNumberOfCurrentStep_value) > 1) 
                or (int(AccIHighStepMaxCurrent_mA_value) == int(AccIHighStepMinCurrent_mA_value) and int(AccIHighNumberOfCurrentStep_value) == 1) 
                and (str(AccIHighStepMinCurrent_mA_value).isdigit() and str(AccIHighStepMaxCurrent_mA_value).isdigit() and str(AccIHighNumberOfCurrentStep_value).isdigit()
                     and int(AccIHighStepMaxCurrent_mA_value)<=15000 and int(AccIHighStepMinCurrent_mA_value)>=100 and int(AccIHighNumberOfCurrentStep_value)<=1000)):
                return True, False, True, False, True, False, "success", "OK"
            return False, True, False, True, False, True, "danger", "Not OK"
        return False, True, False, True, False, True, "danger", "Not OK"
    return False, False, False, False, False, False, "warning", "Check"

@callback(
        Output("AccILowStepMinCurrent_mA", "valid"),
        Output("AccILowStepMinCurrent_mA", "invalid"),
        Output("AccILowStepMaxCurrent_mA", "valid"),
        Output("AccILowStepMaxCurrent_mA", "invalid"),
        Output("AccILowNumberOfCurrentStep", "valid"),
        Output("AccILowNumberOfCurrentStep", "invalid"),
        Output("check_AccILowParameters_button", "color"),
        Output("check_AccILowParameters_button", "children"),
        Input("check_AccILowParameters_button", "n_clicks"),
        State("AccILowStepMinCurrent_mA", "value"),
        State("AccILowStepMaxCurrent_mA", "value"),
        State("AccILowNumberOfCurrentStep", "value")
)
def check_AccILowParameters(n, AccILowStepMinCurrent_mA_value, AccILowStepMaxCurrent_mA_value, AccILowNumberOfCurrentStep_value):
    if n:
        if AccILowStepMinCurrent_mA_value is not None and AccILowStepMaxCurrent_mA_value is not None and AccILowNumberOfCurrentStep_value is not None:
            if ((int(AccILowStepMaxCurrent_mA_value) > int(AccILowStepMinCurrent_mA_value) and int(AccILowNumberOfCurrentStep_value) > 1) 
                or (int(AccILowStepMaxCurrent_mA_value) == int(AccILowStepMinCurrent_mA_value) and int(AccILowNumberOfCurrentStep_value) == 1) 
                and (str(AccILowStepMinCurrent_mA_value).isdigit() and str(AccILowStepMaxCurrent_mA_value).isdigit() and str(AccILowNumberOfCurrentStep_value).isdigit()
                     and int(AccILowStepMaxCurrent_mA_value)<=15000 and int(AccILowStepMinCurrent_mA_value)>=100 and int(AccILowNumberOfCurrentStep_value)<=1000)):
                return True, False, True, False, True, False, "success", "OK"
            return False, True, False, True, False, True, "danger", "Not OK"
        return False, True, False, True, False, True, "danger", "Not OK"
    return False, False, False, False, False, False, "warning", "Check"

# callback that open/close the modal that provides information concerning the test accuracy
@callback(
    Output("info_test_accuracy_modal", "is_open"),
    [Input("info_test_accuracy", "n_clicks"), Input("info_test_accuracy_modal_close", "n_clicks")],
    [State("info_test_accuracy_modal", "is_open")],
)
def toggle_info_test_accuracy_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# callback that display the content of the modal from the file markdown_test_info
@callback(
        Output("info_test_accuracy_modal_content", "children"),
        Input("info_test_accuracy", "n_clicks")
)
def display_info_test_accuracy_modal_content(n):
    if n:
        return dcc.Markdown(markdown_test_info.markdown_test_accuracy)

# creation of the progress bar maximale value for the accuracy test
def calcul_progress_bar_max_accuracy():
    global progress_bar_max_accuracy
    progress_bar_max_accuracy = Settings.json_data["AccNumberOfVHighStep"] + Settings.json_data["AccIHighNumberOfCurrentStep"] + Settings.json_data["AccNumberOfStepInVLowDutySweep"] + Settings.json_data["AccILowNumberOfCurrentStep"] + 2
# initialization of the progress bar maximale value
calcul_progress_bar_max_accuracy()

# callback that launch accuracy test; update the test_accuracy_button and update the test information in the json (JsonTestsHistory_data)
@callback(   
    dash.dependencies.Output("test_accuracy_button", "children"),
    [dash.dependencies.Input("test_accuracy_button", "n_clicks")],
    [dash.dependencies.State("test_accuracy_button", "color"),
     dash.dependencies.State("TestName","value"),
     dash.dependencies.State("LowLeg","value"),
     dash.dependencies.State("BoardSN","value")
     ]
)
def launch_test_accuracy(n, test_accuracy_button, TestName, LowLeg, BoardSN):
    if TestName is None or LowLeg is None or BoardSN is None and n is None:
        raise PreventUpdate
    else:
        if test_accuracy_button == "success":
            if "TestAccuracy" not in Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]:
                Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex].append("TestAccuracy")

            with open("JsonTestsHistory.json", "w") as f:
                json.dump(Settings.JsonTestsHistory_data, f, indent=4)

            Accuracy.MeasureAccuracy(TestName, int(LowLeg))
            return "Accuracy test Done"
        else:
            return "Accuracy test"



#####################################################################################
#                                  Histogram Test                                   #
#####################################################################################

# creation of the histogram test button
test_histogram = dbc.Button(
                "Histogram test", 
                id="test_histogram_button",
                color="danger",
                n_clicks=0,
                ),

# creation of the card that contains the InputTexts to configure the histogram test
Histogram_Test_Parameters = dbc.Card(
            [
                dbc.CardHeader(
                    html.A(
                        "Histogram test parameters",
                        id="histogram_test_parameters_card_header",
                        className="histogram_test_parameters_card_header",
                        style={"textDecoration": "none", "cursor": "pointer"},
                    )
                ),
                dbc.Collapse(
                    dbc.CardBody(
                        [
                        dbc.Button(html.I(className="fas fa-lightbulb", style={"margin_right": "4px"}),
                                    id="info_test_histogram", outline=True, n_clicks=0),
                        dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("Information histogram test")),
                            dbc.ModalBody(id="info_test_histogram_modal_content"),
                            dbc.ModalFooter(
                                dbc.Button(
                                    "Close", id="info_test_histogram_modal_close", className="ms_auto", n_clicks=0
                                )
                            ),
                        ],
                        id="info_test_histogram_modal",
                        size="lg",
                        is_open=False,
                        ),
                        html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Number of samples read per duty (DMM and SPIN) for test Histogram"),
                                    dbc.Input(id="HistNumberOfPointsPerDuty", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Duty cycle for the VHigh measures (percent)"),
                                    dbc.Input(id="HistVHighCalibrationDutyPercent", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Current sink by the load for the VHigh measures (mA)"),
                                    dbc.Input(id="HistVHighCalibrationLowCurrent_mA", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Value of the first VHigh step for VHigh measures (mV)"),
                                    dbc.Input(id="HistStepMinVHigh_mV", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Value of the last VHigh step for VHigh measures (mV)"),
                                    dbc.Input(id="HistStepMaxVHigh_mV", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("Number of VHigh steps for VHigh measures"),
                                    dbc.Input(id="HistNumberOfVHighStep", valid=False, invalid=False, persistence_type='memory', persistence=True),
                                ]
                            ),
                            dbc.Button(
                                "Check",
                                id="check_HistVHighParameters_button",
                                color="warning"
                            ),                            
                        ]
                    ),
                    id="histogram_test_parameters_card_collapse",
                ),
            ],
            id="histogram_test_parameters_card", color = "", outline = True
        )

# callback that open/close the histogram_test_parameters_card
@callback(
    Output("histogram_test_parameters_card_collapse", "is_open"),
    [Input("histogram_test_parameters_card_header", "n_clicks")],
    [dash.dependencies.State("histogram_test_parameters_card_collapse", "is_open")],
)
def toggle_histogram_test_parameters_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# callback that updates the histogram_test_parameters_card color
# in this callback, all parameters that belongs to the histogram test have to be present
@callback(
        Output("histogram_test_parameters_card", "color"),

        Input("HistNumberOfPointsPerDuty", "valid"),
        Input("HistVHighCalibrationDutyPercent", "valid"),
        Input("HistVHighCalibrationLowCurrent_mA", "valid"),
        Input("HistNumberOfVHighStep", "valid"),
        Input("HistStepMinVHigh_mV", "valid"),
        Input("HistStepMaxVHigh_mV", "valid"),
        
        Input("HistNumberOfPointsPerDuty", "invalid"),
        Input("HistVHighCalibrationDutyPercent", "invalid"),
        Input("HistVHighCalibrationLowCurrent_mA", "invalid"),
        Input("HistNumberOfVHighStep", "invalid"),
        Input("HistStepMinVHigh_mV", "invalid"),
        Input("HistStepMaxVHigh_mV", "invalid"),

        Input("HistNumberOfPointsPerDuty", "value"),
        Input("HistVHighCalibrationDutyPercent", "value"),
        Input("HistVHighCalibrationLowCurrent_mA", "value"),
        Input("HistNumberOfVHighStep", "value"),
        Input("HistStepMinVHigh_mV", "value"),
        Input("HistStepMaxVHigh_mV", "value"),
        
        Input("TestNamesLoadParameters", "valid")
)
def update_histogram_test_parameters_card_color(HistNumberOfPointsPerDuty_validity,HistVHighCalibrationDutyPercent_validity, HistVHighCalibrationLowCurrent_mA_validity,
                                        HistNumberOfVHighStep_validity, HistStepMinVHigh_mV_validity, HistStepMaxVHigh_mV_validity,
                                        HistNumberOfPointsPerDuty_invalidity, HistVHighCalibrationDutyPercent_invalidity, HistVHighCalibrationLowCurrent_mA_invalidity,
                                        HistNumberOfVHighStep_invalidity, HistStepMinVHigh_mV_invalidity, HistStepMaxVHigh_mV_invalidity,
                                        HistNumberOfPointsPerDuty_value, HistVHighCalibrationDutyPercent_value, HistVHighCalibrationLowCurrent_mA_value,
                                        HistNumberOfVHighStep_value, HistStepMinVHigh_mV_value, HistStepMaxVHigh_mV_value,
                                        TestNamesLoadParameters_validity):
    if ((HistNumberOfPointsPerDuty_validity and  HistVHighCalibrationDutyPercent_validity and HistVHighCalibrationLowCurrent_mA_validity and
                                        HistNumberOfVHighStep_validity and HistStepMinVHigh_mV_validity and HistStepMaxVHigh_mV_validity) or (TestNamesLoadParameters_validity and not (
                                        HistNumberOfPointsPerDuty_invalidity or HistVHighCalibrationDutyPercent_invalidity or HistVHighCalibrationLowCurrent_mA_invalidity or
                                        HistNumberOfVHighStep_invalidity or HistStepMinVHigh_mV_invalidity or HistStepMaxVHigh_mV_invalidity) and 
                                        HistNumberOfPointsPerDuty_value !="" and  HistVHighCalibrationDutyPercent_value !="" and HistVHighCalibrationLowCurrent_mA_value !="" and
                                        HistNumberOfVHighStep_value !="" and HistStepMinVHigh_mV_value !="" and HistStepMaxVHigh_mV_value !="")):
        return "success"
    return ""

# callback that check the value of histogram test parameters
# write callback like these for every parameters that belongs to your test
@callback(
    Output("HistNumberOfPointsPerDuty", "valid"),
    Output("HistNumberOfPointsPerDuty", "invalid"),
    [Input("HistNumberOfPointsPerDuty", "n_submit"), Input("HistNumberOfPointsPerDuty", "n_blur")],
    State("HistNumberOfPointsPerDuty", "value")
)
def check_HistNumberOfPointsPerDuty_validity(HistNumberOfPointsPerDuty_n_submit, HistNumberOfPointsPerDuty_n_blur, HistNumberOfPointsPerDuty_value):
    if HistNumberOfPointsPerDuty_value and (HistNumberOfPointsPerDuty_n_submit or HistNumberOfPointsPerDuty_n_blur):
        if str(HistNumberOfPointsPerDuty_value).isdigit() and int(HistNumberOfPointsPerDuty_value) >= 1 and int(HistNumberOfPointsPerDuty_value) <= 1000:
            return True, False
        return False, True
    return False, False

@callback(
    Output("HistVHighCalibrationDutyPercent", "valid"),
    Output("HistVHighCalibrationDutyPercent", "invalid"),
    [Input("HistVHighCalibrationDutyPercent", "n_submit"), Input("HistVHighCalibrationDutyPercent", "n_blur")],
    State("HistVHighCalibrationDutyPercent", "value"),
    State("starting_duty_cycle_Percent", "value")
)
def check_HistVHighCalibrationDutyPercent_validity(HistVHighCalibrationDutyPercent_n_submit, HistVHighCalibrationDutyPercent_n_blur, HistVHighCalibrationDutyPercent_value, starting_duty_cycle_Percent_value):
    if HistVHighCalibrationDutyPercent_value and starting_duty_cycle_Percent_value and (HistVHighCalibrationDutyPercent_n_submit or HistVHighCalibrationDutyPercent_n_blur):
        if str(HistVHighCalibrationDutyPercent_value).isdigit() and int(HistVHighCalibrationDutyPercent_value) >= int(starting_duty_cycle_Percent_value) and int(HistVHighCalibrationDutyPercent_value) <= 90:
            return True, False
        return False, True
    return False, False

@callback(
    Output("HistVHighCalibrationLowCurrent_mA", "valid"),
    Output("HistVHighCalibrationLowCurrent_mA", "invalid"),
    [Input("HistVHighCalibrationLowCurrent_mA", "n_submit"), Input("HistVHighCalibrationLowCurrent_mA", "n_blur")],
    State("HistVHighCalibrationLowCurrent_mA", "value")
)
def check_HistVHighCalibrationLowCurrent_mA_validity(HistVHighCalibrationLowCurrent_mA_n_submit, HistVHighCalibrationLowCurrent_mA_n_blur, HistVHighCalibrationLowCurrent_mA_mV_value):
    if HistVHighCalibrationLowCurrent_mA_mV_value and (HistVHighCalibrationLowCurrent_mA_n_submit or HistVHighCalibrationLowCurrent_mA_n_blur):
        if str(HistVHighCalibrationLowCurrent_mA_mV_value).isdigit() and int(HistVHighCalibrationLowCurrent_mA_mV_value) >= 100 and int(HistVHighCalibrationLowCurrent_mA_mV_value) <= 15000:
            return True, False
        return False, True
    return False, False

# Here is a template of callback for the usual case in which the user have to enter a min value, a max value and a number of points.
@callback(
        Output("HistStepMinVHigh_mV", "valid"),
        Output("HistStepMinVHigh_mV", "invalid"),
        Output("HistStepMaxVHigh_mV", "valid"),
        Output("HistStepMaxVHigh_mV", "invalid"),
        Output("HistNumberOfVHighStep", "valid"),
        Output("HistNumberOfVHighStep", "invalid"),
        Output("check_HistVHighParameters_button", "color"),
        Output("check_HistVHighParameters_button", "children"),
        Input("check_HistVHighParameters_button", "n_clicks"),
        State("HistStepMinVHigh_mV", "value"),
        State("HistStepMaxVHigh_mV", "value"),
        State("HistNumberOfVHighStep", "value")
)
def check_HistVHighParameters(n, HistStepMinVHigh_mV_value, HistStepMaxVHigh_mV_value, HistNumberOfVHighStep_value):
    if n:
        if HistStepMinVHigh_mV_value is not None and HistStepMaxVHigh_mV_value is not None and HistNumberOfVHighStep_value is not None:
            if ((int(HistStepMaxVHigh_mV_value) > int(HistStepMinVHigh_mV_value) and int(HistNumberOfVHighStep_value) > 1) 
                or (int(HistStepMaxVHigh_mV_value) == int(HistStepMinVHigh_mV_value) and int(HistNumberOfVHighStep_value) == 1) 
                and (str(HistStepMinVHigh_mV_value).isdigit() and str(HistStepMaxVHigh_mV_value).isdigit() and str(HistNumberOfVHighStep_value).isdigit()
                     and int(HistStepMaxVHigh_mV_value)<=96000 and int(HistStepMinVHigh_mV_value)>=10000 and int(HistNumberOfVHighStep_value)<=1000)):
                return True, False, True, False, True, False, "success", "OK"
            return False, True, False, True, False, True, "danger", "Not OK"
        return False, True, False, True, False, True, "danger", "Not OK"
    return False, False, False, False, False, False, "warning", "Check"

# callback that open/close the modal that provides information concerning the test histogram
@callback(
    Output("info_test_histogram_modal", "is_open"),
    [Input("info_test_histogram", "n_clicks"), Input("info_test_histogram_modal_close", "n_clicks")],
    [State("info_test_histogram_modal", "is_open")],
)
def toggle_info_test_histogram_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# callback that display the content of the modal from the file markdown_test_info
@callback(
        Output("info_test_histogram_modal_content", "children"),
        Input("info_test_histogram", "n_clicks")
)
def display_info_test_histogram_modal_content(n):
    if n:
        return dcc.Markdown(markdown_test_info.markdown_test_histogram)

# creation of the progress bar for the histogram test
def calcul_progress_bar_max_histogram():
    global progress_bar_max_histogram
    progress_bar_max_histogram = Settings.json_data["HistNumberOfVHighStep"]*Settings.json_data["HistNumberOfPointsPerDuty"] + 2
# initialization of the progress bar maximale value
calcul_progress_bar_max_histogram()

# callback that launch histogram test; update the test_histogram_button and update the test information in the json (JsonTestsHistory_data)
@callback(   
    dash.dependencies.Output("test_histogram_button", "children"),
    [dash.dependencies.Input("test_histogram_button", "n_clicks")],
    [dash.dependencies.State("test_histogram_button", "color"),
     dash.dependencies.State("TestName","value"),
     dash.dependencies.State("LowLeg","value"),
     dash.dependencies.State("BoardSN","value")
     ]
)
def launch_test_histogram(n, test_histogram_button, TestName, LowLeg, BoardSN):
    if TestName is None or LowLeg is None or BoardSN is None:
        raise PreventUpdate
    if n is None:
        raise PreventUpdate
    else:
        if test_histogram_button == "success":  

            if "TestHistogram" not in Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]:
                Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex].append("TestHistogram")

            with open("JsonTestsHistory.json", "w") as f:
                json.dump(Settings.JsonTestsHistory_data, f, indent=4)

            Histogram.MeasureHistogram(TestName, LowLeg)

            return "Histogram test Done"
        else:
            return "Histogram test"



#####################################################################################
#                            Calibration coefficents                                #
#####################################################################################

# creation of the card that contains the InputTexts to configure the calibration coefficients
Calibration_Coefficients = dbc.Card(
            [
                dbc.CardHeader(
                    html.A(
                        "Calibration coefficients test parameters",
                        id="calibration_coefficients_card_header",
                        className="calibration_coefficients_card_header",
                        style={"textDecoration": "none", "cursor": "pointer"},
                    )
                ),
                dbc.Collapse(
                    dbc.CardBody(
                        [
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("VLow 1 gain"),
                                    dbc.Input(id="gainV1"),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("VLow 1 offset"),
                                    dbc.Input(id="offsetV1"),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("VLow 2 gain"),
                                    dbc.Input(id="gainV2"),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("VLow 2 offset"),
                                    dbc.Input(id="offsetV2"),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("VHigh gain"),
                                    dbc.Input(id="gainVH"),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("VHigh offset"),
                                    dbc.Input(id="offsetVH"),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("ILow 1 gain"),
                                    dbc.Input(id="gainI1"),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("ILow 1 offset"),
                                    dbc.Input(id="offsetI1"),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("ILow 2 gain"),
                                    dbc.Input(id="gainI2"),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("ILow 1 offset"),
                                    dbc.Input(id="offsetI2"),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("IHigh gain"),
                                    dbc.Input(id="gainIH"),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText("IHigh offset"),
                                    dbc.Input(id="offsetIH"),
                                ]
                            ),
                            html.Div(style={"height": "15px"}),
                            dbc.Button(
                                "Confirm",
                                id="confirm_calibration_coefficients_button",
                                color="warning"
                            ),             
                        ]
                    ),
                    id="calibration_coefficients_card_collapse",
                ),
            ],
            id="calibration_coefficients_card", color = "", outline = True
        )

# callback that open/close the calibration_coefficients_card
@callback(
    Output("calibration_coefficients_card_collapse", "is_open"),
    [Input("calibration_coefficients_card_header", "n_clicks")],
    [dash.dependencies.State("calibration_coefficients_card_collapse", "is_open")],
)
def toggle_calibration_coefficients_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# callback that update the dict CalibrationCoeffs from which values the user chose
@callback(
        Output("confirm_calibration_coefficients_button", "children"),
        Output("confirm_calibration_coefficients_button", "color"),
        Input("confirm_calibration_coefficients_button", "n_clicks"),
        State("gainV1", "value"),
        State("offsetV1", "value"),
        State("gainV2", "value"),
        State("offsetV2", "value"),  
        State("gainVH", "value"),
        State("offsetVH", "value"),
        State("gainI1", "value"),
        State("offsetI1", "value"),
        State("gainI2", "value"),
        State("offsetI2", "value"),  
        State("gainIH", "value"),
        State("offsetIH", "value")
)
def update_CalibrationCoeffs(n, gV1_value, oV1_value, gV2_value, oV2_value, gVH_value, oVH_value,
                             gI1_value, oI1_value, gI2_value, oI2_value, gIH_value, oIH_value):
    if (n and gV1_value is not None and oV1_value is not None and gV2_value is not None and oV2_value is not None and gVH_value is not None and oVH_value is not None and
        gI1_value is not None and oI1_value is not None and gI2_value is not None and oI2_value is not None and gIH_value is not None and oIH_value is not None):

        Settings.CalibrationCoeffs["gV1"]=float(gV1_value)
        Settings.CalibrationCoeffs["oV1"]=float(oV1_value)
        Settings.CalibrationCoeffs["gV2"]=float(gV2_value)
        Settings.CalibrationCoeffs["oV2"]=float(oV2_value)
        Settings.CalibrationCoeffs["gVH"]=float(gVH_value)
        Settings.CalibrationCoeffs["oVH"]=float(oVH_value)
        Settings.CalibrationCoeffs["gI1"]=float(gI1_value)
        Settings.CalibrationCoeffs["oI1"]=float(oI1_value)
        Settings.CalibrationCoeffs["gI2"]=float(gI2_value)
        Settings.CalibrationCoeffs["oI2"]=float(oI2_value)
        Settings.CalibrationCoeffs["gIH"]=float(gIH_value)
        Settings.CalibrationCoeffs["oIH"]=float(oIH_value)
        return "Confirmed", "success"
    return "Confirm", "warning"



#####################################################################################
#                                  Tests collapse                                   #
#####################################################################################

# callback that :
# _ allow the launch of the tests when the setup is completed 
# _ save the test information in a json that contains the information of all test done in history
@callback(
    Output("tests_button", "color"),
    Output("test_efficiency_button", "color"), 
    Output("test_accuracy_button", "color"), 
    Output("test_coefficients_button", "color"),
    Output("test_histogram_button", "color"),
    Output("entire_test_procedure_button", "color"), 
    [Input("experiment_button", "color"),
     Input("instrument_button", "color"),
     Input("TestName", "valid"),
     Input("BoardSN", "valid"),
     Input("LowLeg", "valid"),
     Input("converter_type", "value"),
     Input("power_supply_type", "value"),
     Input("load_type", "value")]
)
def tests_launchable(experiment_button, instrument_button, TestName_validity, BoardSN_validity, LowLeg_validity, 
                     converter_type_value, power_supply_type_value, load_type_value):
    if (experiment_button == "success" and instrument_button == "success" and TestName_validity and BoardSN_validity and LowLeg_validity and converter_type_value
        and power_supply_type_value and load_type_value):
        
        Settings.JsonTestsHistory_data["TestNamesHistory"].append(TestName)
        for i in range(len(Settings.JsonTestsHistory_data["TestNamesHistory"])):
            if Settings.JsonTestsHistory_data["TestNamesHistory"][i] == TestName:
                global TestIndex
                TestIndex=i
        Settings.JsonTestsHistory_data["TestsDoneHistory"].append([])

        Dir = os.path.dirname(os.path.abspath(__file__))
        Dir = os.path.dirname(Dir)
        Dir = os.path.join(Dir, "Results")
        TestFolderPath = os.path.join(Dir, TestName)
        os.makedirs(TestFolderPath, exist_ok=True)
        NewJsonPath = TestFolderPath + "\json_" + TestName + ".json"
        with open(NewJsonPath, 'w') as f:
            json.dump(Settings.json_data, f, indent=4)

        Settings.JsonTestsHistory_data["BoardSNHistory"].append(str(BoardSN))
        Settings.JsonTestsHistory_data["LowLegHistory"].append(LowLeg)
        Settings.JsonTestsHistory_data["EffVHighStepArray_V_History"].append([int(v/1000) for v in Settings.json_data["EffVHighStepArray_mV"]])
        Settings.JsonTestsHistory_data["ConverterTypeHistory"].append(str(converter_type_value))
        Settings.JsonTestsHistory_data["PowerSupplyTypeHistory"].append(str(power_supply_type_value))
        Settings.JsonTestsHistory_data["LoadTypeHistory"].append(str(load_type_value))
        Settings.JsonTestsHistory_data["HistVHighStepArray_mV_history"].append([int(v/1000) for v in Settings.json_data["HistVHighStepArray_mV"]])
        
        with open("JsonTestsHistory.json", "w") as f:
            json.dump(Settings.JsonTestsHistory_data, f, indent=4)
        
        return "success", "success", "success", "success", "success", "warning"
    else :
        return "danger", "danger", "danger", "danger", "danger", "danger"

# callback that open/close the tests_collapse when the user clicks on tests_button
@callback(
          dash.dependencies.Output("tests_collapse", "is_open"),
          [dash.dependencies.Input("tests_button", "n_clicks")],           
          [dash.dependencies.State("tests_collapse", "is_open")],                   
)
def toggle_tests_collapse(n, is_open):
    if n:
        return not is_open
    return is_open



#####################################################################################
#                        All test procedure / progress bar                          #
#####################################################################################

# creation of the entire_test_procedure_button
run_entire_tests_procedure = dbc.Button(
                "Run entire test procedure",
                id = "entire_test_procedure_button",
                color = "danger",
                n_clicks=0,
                style={"width": "50%", "display": "block", "margin": "auto"},
                )

# creation of the variable progress_bar_max_test_sequence
progress_bar_max_test_sequence = progress_bar_max_accuracy + progress_bar_max_efficiency + progress_bar_max_coefficients + progress_bar_max_histogram

# callback which manages the progress bar according to the test chosen and its progress
@callback(Output("progress", "value"), Output("progress", "max"), [Input("progress_interval", "n_intervals")], State("entire_test_procedure_button", "n_clicks"), State("test_histogram_button", "n_clicks"), State("test_efficiency_button", "n_clicks"), State("test_coefficients_button", "n_clicks"), State("test_accuracy_button", "n_clicks"),
          State("entire_test_procedure_button", "children"), State("test_histogram_button", "children"), State("test_efficiency_button", "children"), State("test_coefficients_button", "children"), State("test_accuracy_button", "children"))
def update_progress(n, n_entire_test_procedure_button, n_histogram_test_button, n_efficiency_test_button, n_coefficients_test_button, n_accuracy_test_button, 
                    entire_test_procedure_button_children, histogram_test_button_children, efficiency_test_button_children, coefficients_test_button_children, accuracy_test_button_children):
    if n_entire_test_procedure_button and entire_test_procedure_button_children == "Run entire test procedure":
        current_value = Settings.TestAccuracyProgress + Settings.TestEfficiencyProgress + Settings.TestCoefficientsProgress
        return current_value, progress_bar_max_test_sequence
    elif n_histogram_test_button and histogram_test_button_children == "Histogram test":
        return Settings.TestHistogramProgress, progress_bar_max_histogram
    elif n_efficiency_test_button and efficiency_test_button_children == "Efficiency test":
        return Settings.TestEfficiencyProgress, progress_bar_max_efficiency
    elif n_coefficients_test_button and coefficients_test_button_children == "Coefficients test":
        return Settings.TestCoefficientsProgress, progress_bar_max_coefficients
    elif n_accuracy_test_button and accuracy_test_button_children == "Accuracy test":
        return Settings.TestAccuracyProgress, progress_bar_max_accuracy
    return 0, 0

# callback that launch the entire test sequence and update the test information in the json (JsonTestsHistory_data)
@callback(
        Output("entire_test_procedure_button", "children"),
        Input("entire_test_procedure_button", "n_clicks"),
        [dash.dependencies.State("entire_test_procedure_button", "color"),
        dash.dependencies.State("TestName","value"),
        dash.dependencies.State("LowLeg","value"),
        dash.dependencies.State("BoardSN","value")]
)
def launch_entire_tests_precedure(n, entire_test_procedure_button_color, TestName, LowLeg, BoardSN):
    if TestName is None or LowLeg is None or BoardSN is None and n is None:
        raise PreventUpdate
    else:
        if entire_test_procedure_button_color == "warning":
            if "TestAccuracy" not in Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]:
                Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex].append("TestAccuracy")
            if "TestEfficiency" not in Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]:
                Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex].append("TestEfficiency")
            if "TestCoefficients" not in Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]:
                Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex].append("TestCoefficients")
            if "TestHistogram" not in Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex]:
                Settings.JsonTestsHistory_data["TestsDoneHistory"][TestIndex].append("TestHistogram")

            with open("JsonTestsHistory.json", "w") as f:
                json.dump(Settings.JsonTestsHistory_data, f, indent=4)            
            Coefficients.GetCoefficients(TestName, BoardSN, LowLeg)
            Accuracy.MeasureAccuracy(TestName, LowLeg)
            Efficiency.MeasureEfficiency(TestName, LowLeg)
            Histogram.MeasureHistogram(TestName, LowLeg)
            return "Test Procedure Completed"
        else:
            return "Run entire test procedure"

# creation of the modal that contains the information to run the tests
test_information_modal= dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("Information to run the tests")),
                            dbc.ModalBody(id="test_information_modal_content"),
                            dbc.ModalFooter(
                                dbc.Button(
                                    "Close", id="test_information_modal_close", className="ms_auto", n_clicks=0
                                )
                            ),
                        ],
                        id="test_information_modal",
                        size="lg",
                        is_open=False,
                        )

# callback that open/close the modal that provides information to run the tests
@callback(
    Output("test_information_modal", "is_open"),
    [Input("test_information_button", "n_clicks"), Input("test_information_modal_close", "n_clicks")],
    [State("test_information_modal", "is_open")],
)
def toggle_test_information_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# callback that display the content of the modal from the file markdown_test_info
@callback(  
        Output("test_information_modal_content", "children"),
        Input("test_information_button", "n_clicks")
)
def display_test_information_modal_content(n):
    if n:
        return dcc.Markdown(markdown_test_info.markdown_test_information)



#####################################################################################
#                                      LAYOUT                                       #
#####################################################################################

# display of the layout
layout = html.Div([
    dbc.Container(
        [
            html.H1("Test Bench Setup"),
            dbc.Button(html.I(className="fas fa-lightbulb", style={"margin_right": "4px"}), id="test_information_button", outline=True),
            test_information_modal,
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Name of the Test"),
                                dbc.Input(
                                    id="TestName",
                                    valid=False,
                                    invalid=False,
                                    value=None,
                                    persistence_type='memory',
                                    persistence=True
                                ),
                            ]
                        ),
                    ),
                ],
            ),
            test_name_issue_card,
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Side of the Test"),
                    dbc.Select(
                        id="LowLeg",
                        options=[
                            {"label": "Leg 1", "value": 1},
                            {"label": "Leg 2", "value": 2},
                        ],
                        value=None,
                        valid=False,
                        persistence_type='memory',
                        persistence=True
                    ),
                ]
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Board Serial Number"),
                    dbc.Input(
                        id="BoardSN",
                        value=None,
                        valid=False,
                        invalid=False,
                        persistence_type='memory',
                        persistence=True
                    ),
                ]
            ),
            html.Hr(),
            html.Div([
                dbc.Button(
                    "Instrument Setup", 
                    id="instrument_button",
                    color="danger",
                    n_clicks=0
                ),
                dbc.Collapse(
                    [
                        html.Div(style={"height": "15px"}),
                        dbc.Button(
                            html.I(className="fas fa-lightbulb", style={"margin_right": "4px"}),
                            id="DMM_address_info_button",
                            outline=True
                        ),
                        dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("DMM's address")),
                            dbc.ModalBody(id="DMM_address_modal_content"),
                            dbc.ModalFooter(
                                dbc.Button(
                                    "Close", id="DMM_address_modal_close", className="ms_auto", n_clicks=0
                                )
                            ),
                        ],
                        id="DMM_address_modal",
                        size="lg",
                        is_open=False,
                        ),
                        dbc.Row(
                        [
                        html.Div(style={"height": "15px"}),
                        dbc.Button(
                            "Connect all DMM",
                            id="connect_all_DMM_button",
                            color="warning",
                            className="mx-auto",
                            style={"width": "50%"}
                        ),
                        ],
                    ),
                        dbc.Row(
                        [
                            html.Div(style={"height": "30px"}),
                            dbc.Col(voltage_high, width={"size":4,"offset":2}),
                            dbc.Col(voltage_low, md=4),
                        ],
                        align="center",
                    ),
                        dbc.Row(
                        [
                            dbc.Col(current_high, width={"size":4,"offset":2}),
                            dbc.Col(current_low, md=4),
                        ],
                        align="center",
                    ),
                        html.Div(style={"height": "15px"}),
                        DMMs_on_the_same_ad_card,
                        html.Div(style={"height": "15px"}),
                        dbc.Button(
                            "Close window",
                            id = "close_instrument_collapse_button",
                            color = "warning"
                        ),       
                    ],
                    id="instrument_collapse", 
                    is_open=False,
                ),
            ]),
            html.Hr(),
            html.Div([
                dbc.Button(
                    "Experiment Setup", 
                    id="experiment_button",
                    color="danger",
                    n_clicks=0,
                ),
                dbc.Collapse([
                    dbc.Row(
                        [
                            html.Div(style={"height": "15px"}),
                            dbc.Button(
                            "Connect all Instruments",
                            id="connect_all_instruments_button",
                            color="warning",
                            className="mx-auto",
                            style={"width": "50%"}
                            ),
                        ],
                    ),
                    html.Div(style={"height": "15px"}),
                    dbc.Row(
                        [
                            html.Div(style={"height": "30px"}),
                            dbc.Col(voltage_source, md=4),
                            dbc.Col(power_converter, md=4),
                            dbc.Col(load_device, md=4),
                        ],
                        align="center",
                    ),
                    html.Div(style={"height": "15px"}),
                    load_existing_parameters(),
                    html.Div(style={"height": "15px"}),
                    Global_Parameters,
                    html.Div(style={"height": "15px"}),
                    Coefficients_Test_Parameters,
                    html.Div(style={"height": "15px"}),
                    Efficiency_Test_Parameters,
                    html.Div(style={"height": "15px"}),
                    Accuracy_Test_Parameters,
                    html.Div(style={"height": "15px"}),
                    Histogram_Test_Parameters,
                    html.Div(style={"height": "15px"}),
                    Calibration_Coefficients,
                    html.Div(style={"height": "15px"}),
                    dbc.Col(
                        dbc.Button(
                            "Save all parameters",
                            id = "save_all_parameters_button",
                            color = "warning"
                        ), width={"size": 3, "offset": 0}
                    ),
                    html.Div(style={"height": "15px"}),
                    dbc.Col(
                        dbc.Button(
                            "Close window",
                            id = "close_experiment_collapse_button",
                            color = "warning"
                        ), width={"size": 3, "offset": 0}
                    ),                  
                
                ],
                    id="experiment_collapse",
                    is_open=False,
                ),
            ]),
            html.Hr(),
            html.Div([
                dbc.Button(
                    "Tests", 
                    id="tests_button",
                    color="danger",
                    n_clicks=0,
                ),
                dbc.Collapse(
                    [
                        html.Div(style={"height": "15px"}),
                        run_entire_tests_procedure,
                        dbc.Row(
                            [
                                html.Div(style={"height": "15px"}),
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Procedure of test"),
                                        dbc.CardBody("1 _ Run Coefficients test"),
                                        dbc.CardBody("2 _ Run Accuracy test"),
                                        dbc.CardBody("3 _ Run Efficiency test"),
                                        dbc.CardBody("4 _ Run Histogram test"),
                                        dbc.CardBody("Then, click on the analysis tab to analyze the results obtained"),
                                    ]
                                    ),
                            ],
                        ),
                        dbc.Row(
                            [
                                html.Div(style={"height": "15px"}),
                                dbc.Col(test_coefficients, style={"width": "100%", "display": "block", "margin": "auto"}),
                                dbc.Col(test_accuracy, style={"width": "100%", "display": "block", "margin": "auto"}),
                                dbc.Col(test_efficiency, style={"width": "100%", "display": "block", "margin": "auto"}),
                                dbc.Col(test_histogram, style={"width": "100%", "display": "block", "margin": "auto"}),
                            ],
                            align="center",
                        ),
                        html.Div(style={"height": "15px"}),
                        html.Div(
                            [
                                dcc.Interval(id="progress_interval", n_intervals=0, interval=1000),
                                dbc.Progress(id="progress", value=0, max="progress_bar_max"),
                            ]
                        ),
                    ],
                    is_open=False,
                    id="tests_collapse"
                ),
            ]),
        ],
        fluid=True,
    ),
    dcc.Store(id='dcc_add', data=DMMDict),
])
