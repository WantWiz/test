# Graphical User Interface (GUI)


The Graphical User Interface (GUI) sets up a simple web application using Dash, a Python framework for building interactive web applications with data visualization. The app is called `OwnBench` and consists of two main pages: `Setup` and `Analyse`.

## Main file

This code sets up a basic multi-page web application with a sidebar navigation menu using Dash and Bootstrap, and it provides a way to dynamically update the content based on the URL pathname using callback functions. The application allows users to switch between the `Setup` and `Analyse` pages and handles invalid URLs with a 404 error message.

### Imports

```
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
from pages import side_bar, setup_page, analyse_page
```

The code begins by importing necessary libraries and modules, including Dash, Dash Bootstrap Components (dbc), and specific components from Dash (Input, Output, dcc, html).

### Creation of the application

```
app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)
```

Then, it creates an instance of the Dash application, setting the external stylesheets to use Bootstrap for styling and Font Awesome for icons. suppress_callback_exceptions=True is set to handle exceptions when navigating between pages.

### Creation of components

```
content = html.Div(id="page-content", className="content")

DMMDict = [{'Meas':'IHigh', 'DMM address' : None},
           {'Meas':'VHigh', 'DMM address' : None},
           {'Meas':'ILow', 'DMM address' : None},
           {'Meas':'VLow', 'DMM address' : None}]

server = app.server

logo_path = app.get_asset_url('logo_owntech_small.png')

sidebar = html.Div

    ...
```

1. It defines the content layout for the application using a Div element with the ID `page-content`. This element will hold the content of the currently active page.

2. It creates a list of dictionaries called DMMDict, which contains information about different measurements and their corresponding DMM (Digital Multimeter) addresses.

3. It sets the server variable to app.server. This is required to deploy the application on a production server.

4. It loads the logo image for the sidebar and define the layout for the sidebar using HTML and Bootstrap components. The sidebar contains a logo, the title `OwnBench`, and navigation links for `Setup` and `Analyse` pages.

### Layout

```
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])
```

It defines the main layout of the application, including the sidebar and the content area, using a Div element. The navigation links will be used to update the content based on the current URL pathname.

### Callback

```
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page_content(pathname):
    if pathname == "/":
        return setup_page.layout
    elif pathname == "/analyse":
        return analyse_page.layout
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )
```

It implements a callback function that updates the content based on the URL pathname. When the user clicks on a navigation link, the URL pathname changes, and the corresponding page content is displayed. If the URL pathname is not recognized (e.g., an invalid URL), a `404: Not found` message is displayed.

### Run Dash server

```
if __name__ == "__main__":
    app.run_server(debug=True, port=8888)
```

Finally, the code runs the Dash server on port 8888.

## Setup page

## Imports / Initializations

Firstly, we import necessary libraries and modules, including Dash, Dash Bootstrap Components (dbc), pandas, plotly.graph_objs, scikit-learn (sklearn), and others.
Then, the variables LowLeg, TestName, VHighTab_V, BoardSN, converter_values_tab, and TestIndex are initialized with default values to be used later in the setup_page.
Afterwards, the code sets up the path to the `Libraries` folder and imports various custom libraries and modules from that folder. These custom modules likely contain functions and utilities used in the application, such as handling instruments, plotting, data management, and more.
Enventually, the code creates a pyvisa.ResourceManager() instance, which will be used for interfacing with the instruments.

## Test Information


This code contains the creation of test_name_issue_card and several callback functions used in the setup page of a Dash web application. 

Here's a brief summary of each part:

test_name_issue_card: It creates a card with an empty CardBody and an ID `test_name_issue_card`. This card will be used to display an error message if the entered test name is not valid or already exists.

validate_test_name: This callback function is triggered by the submit and blur events of the `TestName` input field. It validates the entered test name and checks if it is unique. If the test name is invalid or already exists in the test history, appropriate flags are returned to update the input field's validity status. The function also updates the global variable `TestName` if the test name is valid.

update_lowleg_validity: This callback function is triggered whenever the `LowLeg` input field's value changes. It updates the global variable `LowLeg` with the new value and returns a validity status of True if the value is not None.

update_boardsn_validity: This callback function is triggered whenever the `BoardSN` input field's value changes. It updates the global variable `BoardSN` with the new value and returns validity status based on whether the value is a non-negative integer or not.

These callback functions are used to validate user inputs, update global variables based on the input values, and provide visual feedback to users if there are any issues with the entered data on the setup page of the web application.

### Instrument Setup

This code sets up cards and callback functions related to connecting and configuring Digital Multimeters (DMMs) in the setup page of a Dash web application. 
Here's a brief overview of each part:

1. **DMMDict**: This is a list of dictionaries representing different measurements (e.g., `IHigh`, `VHigh`, `ILow`, `VLow`) and their corresponding DMM addresses (initially set to None).

2. **DMM_store**: This DataFrame is created by transforming the `DMMDict` into a DataFrame. It will be used for storage related to the DMMs.

3. **voltage_high, current_high, voltage_low, current_low**: These are different cards created using Dash Bootstrap Components. Each card represents a DMM connection setup for different measurements (e.g., voltage_high for `VHigh`, current_high for `IHigh`, etc.). They include dropdowns to select the DMM address and buttons to indicate the connection status.

4. **voltage_high, current_high, voltage_low, current_low @callbacks**: Each of the cards sets up a callback function (`@callback`) to handle the DMM type selection (`vhigh_dmm_type`, `ihigh_dmm_type`, `vlow_dmm_type`, `ilow_dmm_type`) and updates the respective `Settings` variables (`Settings.VHighGPIBAddress`, `Settings.IHighGPIBAddress`, `Settings.VLowGPIBAddress`, `Settings.ILowGPIBAddress`) based on the selected DMM address. This ensures that the selected DMM addresses are stored and available for further use in the application.

Additionally, there is a callback function (`check_DMMs_on_the_same_ad_card`) to check whether two DMMs are on the same address. If any of the dropdowns (`vhigh_dmm_type`, `ihigh_dmm_type`, `vlow_dmm_type`, `ilow_dmm_type`) have the same selected value, a warning message will be displayed in the `DMMs_on_the_same_ad_card` card.

5. **toggle_instruments_collapse**: This callback function is triggered by button clicks (`instrument_button` or `close_instrument_collapse_button`) and is responsible for opening/closing a collapsible section to display the DMM connection cards.

6. **connect_all_DMM**: This callback function is triggered by button clicks related to connecting DMMs (e.g., `connect_all_DMM_button`, `vlow_button`, `ilow_button`, `vhigh_button`, `ihigh_button`). It updates the connection status for the corresponding DMM cards and returns the updated status and colors for the buttons and cards.

7. **all_DMM_connected**: This callback function is triggered by changes in the connection status of individual DMM cards. It updates the `instrument_button` with the text `Instrument Setup completed` and changes its color to `success` when all DMMs are successfully connected.

8. **toggle_DMM_address_modal** callback: When he user clicks on the icon, the callback display/hide the modal that provides information concerning DMMs.

9. **display_DMM_address_info_modal_content** callback: When the icon button is clicked, the callback returns the content of the modal as a `dcc.Markdown` component with the content from the `markdown_test_info.markdown_DMM_address_info` variable. This content is displayed inside the modal to provide information about the DMMs.

Overall, this code handles the setup and configuration of DMM connections in the setup page of the web application. It allows users to select the DMM type, connect the DMMs, and displays the overall status of DMM connections through the `instrument_button`.

### Experiment Setup

This code sets up cards and callback functions related to connecting and configuring various instruments in the setup page of a Dash web application. 
Here's a brief overview of each part:

1. **power_converter**: This card represents the power converter (DUT) setup. It includes a dropdown to select the converter type, another one to select the port on which it's connected and a button to indicate the connection status.

2. **voltage_source**: This card represents the voltage source setup. It includes a dropdown to select the power supply type, another one to select the port on which it's connected and a button to indicate the connection status.

3. **load_device**: This card represents the load setup. It includes a dropdown to select the load type and a button to indicate the connection status.

4. **check_port_power_converter_validity and check_port_voltage_source_validity** callbacks:
These callbacks check whether the entered port value (`port_power_converter_value` and `port_voltage_source`) exists in the list of possible port names for both Windows (`COM_list`) and Linux (`port_list`) systems. If the entered value is found in either of these lists, it means the port is valid, and the Settings variable `STLINKCommPort` is updated with the entered value.

5. **check_NumberOfStepInDutySweep_validity, check_LoadInternalSafetyCurrent_A_validity, check_LoadInternalSafetyPower_W_validity, check_NumberOfPointsPerDuty_validity, check_duty_step_Percent_validity, check_starting_duty_cycle_Percent_validity**: These callback functions validate the input values of various global parameters related to the tests. They check whether the provided values are within certain limits and update the validity status of the respective input fields accordingly.

6. **toggle_global_parameters_collapse**: This callback function is triggered by button clicks and is responsible for opening/closing the collapsible section to display the global parameters input fields.

7. **update_global_parameters_card_color**: This callback function updates the color of the global parameters card based on the validity of the input values. When all global parameters are valid, the card color is set to `success`.

8. **Global_Parameters**: This card contains input fields for configuring global parameters related to the tests, such as maximum load current, maximum load power, number of samples, etc. It includes a collapsible section to hide/display these fields. Moreover it includes a button icon that display a modal when the user clicks on it.

9. **toggle_info_global_parameters_modal** callback: When he user clicks on the icon, the callback display/hide the modal that provides information concerning global parameters.

10. **display_info_global_parameters_modal_content** callback: When the icon button is clicked, the callback returns the content of the modal as a `dcc.Markdown` component with the content from the `markdown_test_info.markdown_info_global_parameters` variable. This content is displayed inside the modal to provide information about the global parameters.

11. **toggle_experiment_collapse**: This callback function is triggered by button clicks and is responsible for opening/closing the collapsible section to display the experiment setup cards.

12. **connect_all_instruments**: This callback function is triggered by button clicks related to connecting instruments (e.g., `power_source_button`, `converter_button`, `load_button`, `connect_all_instruments_button`). It updates the connection status for the corresponding instrument cards and returns the updated status and colors for the buttons and cards.

13. **exp_setup_completed**: This callback function is triggered by changes in the connection status of individual instrument cards and the `save_all_parameters_button`. It updates the `experiment_button` when all instruments are successfully connected and all parameters are saved.

Overall, this code handles the setup and configuration of various instruments in the setup page of the web application. It allows users to select instrument types, connect the instruments, and configure global test parameters before starting the experiment.

### Json Tests History & test pameters data

This part of the code handles the loading and saving of parameters in JSON format. 
The script has a few main components:

1. `lister_fichiers_dossier(PathFolder)` function: This function takes a folder path as input and attempts to list the files in that folder using `os.listdir()`. If the folder does not exist, it returns an empty list.

2. `update_JsonTestsHistory()` function: This function updates the JSON file `JsonTestsHistory.json` based on the existing folders and the `Settings.JsonTestsHistory_data`. It deletes the default parameters, finds the indexes of tests without associated folders, and updates the relevant entries in `Settings.JsonTestsHistory_data`. Finally, it saves the updated data to `JsonTestsHistory.json`.

3. `uptade_all_json_data()` function: This function is a callback function that triggers when the user clicks on a button (`save_all_parameters_button`). It saves all the parameters provided by the user in the respective entries of `Settings.json_data`.

### Load existing parameters

This part of the script allows the user to load parameters from a test that already be done.

1. `load_existing_parameters()` function: This function creates an input group containing a dropdown (`TestNamesLoadParameters`) to allow the user to choose a test from which they want to load existing parameters.

2. `load_parameters(TestNamesLoadParameters_value)` function: This is triggered when the user selects a test name from a dropdown (`TestNamesLoadParameters`). It loads the parameters of the selected test from the corresponding JSON file and returns the parameter values for different components.

### Coefficients test

This part of the code defines several components, callbacks, and utility functions for the `coefficients test` within the web application. The page contains input fields, buttons, and validation functions to configure and run the test.

Here is a summary of the components and callbacks present in the code:

**Components:**

1. `test_coefficients`: Button to trigger the coefficients test.
2. `Coefficients_Test_Parameters`: A collapsible card that contains input fields for configuring the coefficients test and an icon button to display a modal that contains the information on the test coefficients.
3. Various input fields for specifying test parameters such as `Number of twist averaged twist samples,` `Duty cycle for the calibration of VHigh,` `Current drawn on the low side for the calibration of VHigh,` and more.

**Callbacks:**

1. `toggle_coefficients_test_parameters_collapse`: Toggles the visibility of the `Coefficients_Test_Parameters` card.
2. `update_coefficients_test_parameters_card_color`: Updates the color of the `Coefficients_Test_Parameters` card based on the validity of input fields.
3. Various validation callbacks for input fields (e.g., `check_CoeffNumberOfTWISTMeas_validity`, `check_CoeffVHighCalibrationDutyPercent_validity`, etc.).
6. `launch_test_coefficients`: Callback to launch the coefficients test when the `test_coefficients_button` is clicked.

9. **toggle_info_test_coefficients_modal** callback: When he user clicks on the icon, the callback display/hide the modal that provides information concerning the coefficients test.

7. **display_info_test_coefficients_modal_content** callback: When the icon button is clicked, the callback returns the content of the modal as a `dcc.Markdown` component with the content from the `markdown_test_info.markdown_test_coefficients` variable. This content is displayed inside the modal to provide information about the test coefficients.

### Efficiency/Accuracy/Histogram Tests

The same structure of code is used for the 3 other tests Efficiency test, Accuracy test and Histogram test.

This code section sets up a card with input fields for configuring calibration coefficients. It provides a collapsible card that allows users to adjust calibration coefficients and confirm their settings.

### Calibration coefficents

1. **Calibration_Coefficients Card**: This card contains multiple input fields (Input components) for configuring the calibration coefficients. Each input field corresponds to a specific calibration coefficient, such as gain and offset values for different voltage and current measurements.

2. **toggle_calibration_coefficients_collapse Callback**: This callback controls the opening and closing of the calibration_coefficients_card when the user clicks on the header element (`calibration_coefficients_card_header`).

3. **update_CalibrationCoeffs Callback**: This callback is responsible for updating the calibration coefficients based on the values entered by the user and confirming the changes.
When the "Confirm" button is clicked and all input fields have valid values, the callback updates the `Settings.CalibrationCoeffs` dictionary with the new calibration coefficients based on the user's input.

In summary, this section implements a collapsible card that provides users with input fields to configure calibration coefficients for voltage and current measurements. Users can modify these coefficients and then click the "Confirm" button to save the changes, which are reflected in the `Settings.CalibrationCoeffs` dictionary.

### Tests collapse

This part of the code consists of two separate callback functions. 
Let's break down each function and understand their purpose:

1. `tests_launchable` Callback Function:
   This callback determines whether the tests can be launched based on various input conditions and stores test information in a JSON file containing the history of all tests done.
   To enable test launch, the experiment and instrument setup have to be completed and the test name, the boardSN, the LowLeg, the converter type, the power supply and the load type have to be fixed and valid.

2. `toggle_tests_collapse` Callback Function:
   This callback opens or closes the `tests_collapse` component when the user clicks on the `tests_button`.

### All test procedure / progress bar

1. Creation of the button `run_entire_tests_procedure`.

2. The variable `progress_bar_max_test_sequence` is calculated by summing up the values of `progress_bar_max_accuracy`, `progress_bar_max_efficiency`, `progress_bar_max_coefficients`, and `progress_bar_max_histogram`.

3. Callback Function: `update_progress`
   This callback manages the progress bar according to the test chosen and its progress. Indeed, it calculates the progress value and maximum value for the progress bar based on which test button is clicked.

4. Callback Function: `launch_entire_tests_precedure`
   - This callback launches the entire test sequence and updates the test information in a JSON file (`JsonTestsHistory_data`).
   - It checks if the conditions for launching the test procedure are met and then initiates the appropriate tests.

5. **test_information_modal**:
   - This is the definition of the modal component using `dbc.Modal`.
   - The modal is initially set to be closed (`is_open=False`), meaning it won't be visible when the page loads.

6. **toggle_test_information_modal Callback**: This callback is responsible for opening and closing the test_information_modal when the user interacts with certain elements.

7. **display_test_information_modal_content Callback**: This callback displays the content to be shown in the modal (`test_information_modal_content`) when the user clicks the icon button.

In summary, these callbacks manage the progress bar based on the chosen test and its progress, handle the launch and completion of the entire test procedure, update the test history in a JSON file, and create a modal that provides important information about how to run the tests. When the user clicks the "Information" button, the modal pops up with the relevant details.

### Layout

Here's a brief explanation of its structure:

1. The layout starts with a `html.Div`, containing a `dbc.Container` to hold the entire content of the application.

2. The first section includes the icon button to get information, the test name input field, test name issue card, low leg selection dropdown, and board serial number input field.

3. The next section is for instrument setup, containing buttons and options to connect all digital multimeters (DMMs) and set up voltage and current parameters.

4. The experiment setup section follows, with buttons to connect all instruments and options for voltage source, power converter, and load device setup. It also includes several test parameter sections such as global parameters, coefficients test parameters, efficiency test parameters, accuracy test parameters, and histogram test parameters.

5. The test section comes next, with a button to run the entire test procedure, and details about the test procedure in a card. It also includes buttons to run individual tests for coefficients, accuracy, efficiency, and histogram.

6. A progress bar is displayed to show the progress of the test procedure or individual tests.

Overall, this layout provides a structured interface to set up a test bench, run tests, and monitor the progress of the tests using a web application. The functionality of the application is driven by the interactions with the various input components and callbacks associated with them.

## Analyse page

### Imports / Initializations

This part of the "analyse" page is the import and initialization section. It imports required libraries and initializes variables and data structures used in the analysis process. Here's a brief explanation:

1. **Imports**: This section imports various libraries and modules required for data analysis, visualization, and communication with instruments.

2. **Initialization of Variables**: This section initializes variables used in the analysis process, such as `NumberOfEfficiencyGraphs`, `NumberOf3dEfficiencyGraphs`, `TestIndex`, and various `my_plots` dictionaries. These `my_plots` dictionaries are used to store information about different plots generated during analysis, such as their titles, figure objects, z-axis minimum and maximum values, plot and slider IDs, and input IDs for setting plot limits.

3. **histo_results_active_button_index**: This variable is used to determine the active button for displaying histogram test results.

4. **initialyseplots()**: This is a function used to initialize the `my_plots` dictionaries. It resets these dictionaries to empty, clearing any previous data stored in them.

Overall, this section prepares the necessary tools and data structures required for data analysis and visualization on the "analyse" page of the application.

### Coefficients test

This part of the "analyse" page is related to the "Coefficients Test" section, which handles the display and analysis of calibration coefficients obtained from the tests. Here's a brief explanation of each part:

1. **DisplayLayoutCoeffs()**: This function creates the layout for displaying calibration coefficients results. It reads data from a CSV file containing calibration coefficients and creates a table to display the coefficients, their mean values, and distances from the mean values in terms of standard deviations. The function also calls `PlotTestsHistoCoeffsHistory()` to display a historical plot of calibration coefficients.

2. **PlotTestsHistoCoeffsHistory()**: This function is responsible for plotting the historical data of calibration coefficients.

3. **PDFCoefficientsTest()**: This function is used to generate a page in the PDF report specifically for presenting the calibration coefficients results. It retrieves the calibration coefficients data from a CSV file, prepares the data for the table, and adds the table to the PDF report.

4. **coefficients_results_collapse()**: This callback controls the display of the coefficients results section. When the "results_coefficients_button" is clicked and the test name is valid, it calls the `DisplayLayoutCoeffs()` function to generate the layout for displaying the calibration coefficients. It also toggles the visibility of the results section using the `results-coefficients-collapse` component.

In summary, this part handles the display and analysis of calibration coefficients obtained from the tests. It creates a layout to show the coefficients in a table, plots historical data of calibration coefficients, and generates a dedicated page in the PDF report to present the calibration coefficients results.

### Efficiency test

This part of the "analyse" page is related to the "Efficiency Test" section, which handles the display and analysis of efficiency results. Here's a brief explanation of each part:

1. **createPlotLayoutEff()**: This function is responsible for creating the layout to display efficiency results. It takes parameters like the title, figure, and z-axis minimum and maximum values for each plot. It generates a series of graphs and associats all 3D graphs with a slider for controlling the z-axis range.

2. **PDFEfficiencyTest()**: This function creates a dedicated page in the PDF report to present the efficiency test results. It includes an image that contains 2D efficiency graphs.

3. **plot_interactive_graphs(TestIndex)**: This function is used to create graphs from the efficiency test results associated with the test chosen by the user. It processes data from CSV files, performs computations, and calls various functions from the `InteractivePlot` module to generate interactive 3D plots and other efficiency-related graphs.

4. **efficiency_results_collapse()**: This callback controls the display of the efficiency results section. When the "results_efficiency_button" is clicked and the test name is valid, it calls the `createPlotLayoutEff()` function to generate the layout for displaying efficiency plots. It also toggles the visibility of the results section using the `results-efficiency-collapse` component.

5. **update_zaxis_range()**: These callbacks are responsible for updating the z-axis range of the 3D efficiency graphs when the associated sliders' values change. They are used to enable interactive control of the 3D plot view.

In summary, this part handles the display and analysis of efficiency test results. It creates a layout to show multiple efficiency graphs, including 3D plots with interactive z-axis range sliders. It also generates a dedicated page in the PDF report to present the efficiency test results, including images of 2D efficiency graphs.

### Accuracy test

This part of the "analyse" page is related to the "Accuracy Test" section, which handles the display and analysis of accuracy test results. Here's a brief explanation of each part:

1. **DisplayPlotLayoutAcc()**: This function creates the layout to display the accuracy test results. It reads two images (plots) related to the absolute and relative errors from the accuracy test results. It then decodes the images to base64 format and displays them.

2. **PDFAccuracyTest()**: This function creates a dedicated page in the PDF report to present the accuracy test results. It adds the title includes an image that contains the the plot for the relative error.

3. **accuracy_results_collapse()**: This callback controls the display of the accuracy results section. When the "results_accuracy_button" is clicked and the test name is valid, it calls the `DisplayPlotLayoutAcc()` function to generate the layout for displaying accuracy plots. It also toggles the visibility of the results section using the `results-accuracy-collapse` component.

In summary, this part handles the display and analysis of accuracy test results. It creates a layout to show two images representing the absolute and relative errors from the accuracy test. It also generates a dedicated page in the PDF report to present the accuracy test results, including the plot for the relative error.

### Histogram test

This part of the "analyse" page is related to the "Histogram Test" section, which handles the display and analysis of histogram test results. Let's go through each function and callback in this section:

1. **PlotHistogram()**: This function generates the histogram plots and related data. It reads the data from a CSV file associated with the test and then calls `Plot.PlotHistoDistrib()` to create the histogram plot. Additionally, it calculates the mean and standard deviation of the histogram data and stores them in `Settings.HistMeanStandardDeviationDict`. It also creates another plot for displaying the historical distribution of the TWIST coefficients and stores it in `my_plots_histo_history`.

2. **PDFHistogramTest()**: This function adds a new page to the PDF report dedicated to presenting the histogram test results. It includes an image containing the histogram plot from the test results. It also adds a table that displays the mean value and standard deviation for each measure.

3. **DisplayLayoutHist()**: This function creates the layout for displaying the histogram test results. It takes the histogram plot, its title, and axis range as inputs. It returns a container containing the histogram plot, a table showing the mean and standard deviation for each measure, a plot showing the historical distribution of the TWIST coefficients, and another table displaying the mean and standard deviation of historical the TWIST coefficients.

4. **histogram_results_collapse()**: This callback controls the display of the histogram test results section. When the "results_histogram_button" is clicked, and the test name is valid, or when the number of X-axis divisions is submitted or blurred, or when the button group for test histogram voltage choice is clicked, it calls the `PlotHistogram()` function to generate the histogram plots and related data. Then, it returns the layout for displaying the histogram test results and toggles the visibility of the results section using the `results-histogram-collapse` component.

5. **check_HistNumberOfXAxisDivision_validity()**: This callback checks and updates the value input by the user concerning the accuracy of the histogram (number of X-axis divisions). It ensures that the value is a valid positive integer between 1 and 10000.

6. **DisplayTableOfMeanAndStandartDeviationValues(MeanStandardDeviationDict)**: This function creates a table that displays the mean value and standard deviation for each measure. It takes the `MeanStandardDeviationDict` as input, which contains the mean and standard deviation values for various measures.

7. **buttons_for_test_histo_voltage_choice()**: This function generates the button group for selecting the voltage choice in the histogram test. It creates buttons for each voltage step associated with the test.

8. **update_button_group()**: This callback updates the button group for the test histogram voltage choice. When a button in the group is clicked or when the test name is valid, it calls `buttons_for_test_histo_voltage_choice()` to update the button group based on the current active button index.

In summary, this part handles the display and analysis of histogram test results. It creates the histogram plots, generates a dedicated page in the PDF report to present the histogram test results, and provides a layout to display the histogram plots, mean values, standard deviations, and historical distribution of the TWIST coefficients. It also includes validations for user input concerning the number of X-axis divisions and handles the selection of voltage choices for the histogram test.

### Results report

This part of the "analyse" page is responsible for generating a results report in PDF format based on the test data and results obtained during the analysis. Let's go through each part of this section:

1. **ResultsReportCard** This card includes a title, a brief description, and a button labeled "Generate Results Report." 

2. **PDFCreation()** This function creates the PDF report. It uses the FPDF library, a Python library for working with PDF files. The function starts by creating a new PDF object (`pdf = FPDF()`). It then adds a new page and sets the font style and size for the title. The function populates the PDF with various pieces of information, such as test name, test parameters, and the results of various tests (e.g., TestCoefficients, TestAccuracy, TestEfficiency, and TestHistogram) according to which one have been done.

3. **generate_report()** This callback is triggered when the "generate_results_button" is clicked and the test name is valid. It calls the `PDFCreation()` function to generate the PDF report. After the report is generated, the function returns the text "PDF Created," which is displayed on the button.

To summarize, the "Results Report" section contains a card with a button to generate the PDF report. When the button is clicked and the test name is valid, the PDF report is created using the `PDFCreation()` function, and the button text changes to "PDF Created." The generated PDF report includes test information, parameters, and results of various tests performed during the analysis.

### Test results

This part of the "analyse" page includes functions and callbacks related to displaying test results.

1. **refresh_TestNamesResultsOptions()**: This function is responsible for creating a list of options for the "TestNameAnalysis" dropdown. Indeed, it extracts the test names from the `Settings.JsonTestsHistory_data["TestNamesHistory"]`.

2. **refresh_history()**: This callback calls the `refresh_TestNamesResultsOptions()` function to update the list of test names that can be selected.

3. **load_results_input()**: This function creates an input element that allows the user to choose which test results they want to display. It uses the options generated by the `refresh_TestNamesResultsOptions()` function to populate the dropdown list.

4. **test_name_analysis_validity()**: This callback is triggered when the user selects a test name from the dropdown input ("TestNameAnalysis"). It checks the validity of the selected test name by ensuring it is present in the list of test names (`Settings.JsonTestsHistory_data["TestNamesHistory"]`). If the test name is valid, the global variable `TestIndex` is updated to store the index of the selected test in the `Settings.JsonTestsHistory_data` dictionnary.

5. **results_displayable_collapse()**: This callback is triggered when the validity of the test name is determined in the `test_name_analysis_validity()` callback. If the test name is valid, this callback checks the number of tests done in the selected test using the `Settings.JsonTestsHistory_data["TestsDoneHistory"]` dictionary. Depending on the tests done, it returns a message indicating which test results can be displayed for the chosen test.

6. **PlotTestsHistoCoeffsHistory()**: This function is responsible for generating graphs for coefficient test data and histogram test data. It uses the `Plot.py` file to create these graphs based on the arguments passed to it.

7. **DisplayLayoutTestsHistoCoeffsHistory()**: This function is used to display the graphs generated by the `PlotTestsHistoCoeffsHistory()` function. It takes the title, figure, zMin, and zMax as arguments and uses them to create a layout with the graph and other components for displaying test data.

In summary, this section manages the selection and display of test results. It includes a dropdown input that allows users to choose a test name and see the available test results. When a test name is selected, it triggers callbacks to check the validity of the selected test name and display the corresponding test results. The results can include graphs for coefficient test data and histogram test data, which are generated and displayed using custom functions.

### LAYOUT

The layout of the "analyse" page consists of a series of collapsible sections for displaying different types of test results. Each section is associated with a button that triggers the expansion or collapse of the respective content. Below is a breakdown of the layout:

1. **Header**: The page starts with an "Analysis" heading.

2. **Load Results Input**: This section contains an input element for selecting the test results to display. It is created using the `load_results_input()` function and includes a dropdown (`dbc.Select`) populated with available test names.

3. **Results Displayable Collapse**: This section shows a message indicating which test results can be displayed for the selected test. It is initially collapsed and expands only when a valid test name is selected from the dropdown. It is created using `dbc.Collapse` and updated by the `results_displayable_collapse()` callback.

4. **Results Coefficients Section**: This section contains a button labeled "Results Coefficients" (`dbc.Button`). When clicked, it reveals the results for coefficients tests. The content is initially hidden and expands upon button click (`dbc.Collapse`). The results content is updated using the `results_coefficients_button` click event and populated by the `coefficients_results` callback.

5. **Results Accuracy Section**: Similar to the "Results Coefficients" section, this section includes a button and a collapsible area for displaying results related to accuracy tests. The results content is updated using the `results_accuracy_button` click event and populated by the `accuracy_results` callback.

6. **Results Efficiency Section**: This section is analogous to the previous two sections but is focused on displaying efficiency test results. The results content is updated using the `results_efficiency_button` click event and populated by the `efficiency_results` callback.

7. **Results Histogram Section**: This section deals with displaying histogram test results. It includes a button to trigger expansion and a collapsible area for displaying the histogram results. The "HistNumberOfXAxisDivision" input allows users to specify the number of x-axis divisions in the histogram. The content is updated using the `results_histogram_button` click event and populated by the `histogram_results_collapse` callback.

8. **Results Report Card**: This section contains a card (`dbc.Card`) titled "Results Report". It includes a button labeled "Generate Results Report". When clicked, it triggers the `generate_report` callback to create a PDF report containing the test results. The PDF report is generated and opened in a new tab.

Overall, the layout organizes the different sections for displaying test results in a structured manner. Users can interact with the page to select specific test results and generate a PDF report for analysis purposes.