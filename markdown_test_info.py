markdown_test_efficiency = """
Here is a describtion of the process for the characterization of the efficiency of the converter:

### Explanation of the test

The idea behind the efficiency test is to measure the efficiency of the card for several values of VHigh. 
The process involves first selecting a specific value for VHigh. 
Then, ILow is set, and VLow is varied. This process is iterated while incrementing ILow each time. 
Once all the ILow values have been scanned, the procedure is repeated for all the chosen values of VHigh. 
By doing this, you can evaluate the efficiency of the card across different VHigh, VLow and ILow combinations.

### Custom test

You can customize the test by fixing several parameters. 
- You can set the value of the number of times to increase the duty sweep for one IHigh value. 
The larger this value is, the more VLow values can be measured for each ILow value. 
This allows you to have a finer resolution and gather more data points for each specific combination of IHigh and ILow.
- You can also choose the values of IHigh, which will, in turn, determine the values of ILow.
- Lastly, you can select the voltage points at which you want to position your measurements. 
However, it's essential to note that choosing a large number of voltage points will significantly increase the duration of your test.

### Output

The script generates the following files: 

|           File           |                                             Description                                             |
|:------------------------:|:---------------------------------------------------------------------------------------------------:|
|    testname_VHigh.csv    | csv file containing every variable monitored during the test                                        |
|  testname_VHigh_AVGD.csv | csv file containing variable monitored, averaged with the value NumberOfpointsPerDuty (settings.py) |
|    testname_histo.svg    | svg containing the distribution of every monitored variable                                         |
|    testname_Eff2D.png    | The efficiency on a 2-D projection, it concatenates every VHigh measures of the test                |
|    testname_Eff2D.svg    | Same as above but in svg                                                                            |
|   testname_3d_plot.html  | The efficiency on 3D, it concatenates every VHigh measures of the test                              |
| testname_3d_rel_err.html | The relative error on efficiency measure in 3D                                                      |
| testname_3d_rel_abs.html | The absolute error on efficiency measure in 3D                                                      |

"""

markdown_test_accuracy ="""

Describtion of the process for the characterization of the accuracy of the converter:

### Explanation of the test

The goal of this test is to assess the measurement of the accuracy of the TWIST for each parameter. 
To achieve this, the idea is to systematically vary the quantities measured by the TWIST one by one. 
For each point and each parameter, the measured values from the TWIST will be compared to the values measured by the DMMs. 
This comparison will help evaluate how accurate the TWIST is in its measurements for different parameters and operating points.

### Custom test

For the measure of each parameters, you can fix many parameters.

- For the VHigh, IHigh and ILow measures, you can set the value of the duty cycle (which affects the low-side voltage), the value of the current sink by the load, as well as the range of values for VHigh, IHigh and ILow. 
Increasing the range of values will improve the precision of the test, but it will also make the test longer.
- For the VLow measure, you can set the values for VHigh, the current sink by the load, and the number of steps.

### Output

The script generates output in the folder 'Output_Accuracy' created in a folder named as you named your test (this folder will be created in the folder Results).

The script generates the following files: 

|               File               |                                   Description                                  |
|:--------------------------------:|:------------------------------------------------------------------------------:|
| TestName_AvgNum_All_Abs.png      | png file containing graph of all absolute errors (VHigh, VLow, IHigh and Ilow) |
| TestName_AvgNum_All_Abs.svg      | svg file containing graph of all absolute errors (VHigh, VLow, IHigh and Ilow) |
| TestName_AvgNum_All_Rel.png      | png file containing graph of all relative errors (VHigh, VLow, IHigh and Ilow) |
| TestName_AvgNum_All_Rel.svg      | svg file containing graph of all relative errors (VHigh, VLow, IHigh and Ilow) |
|  TestName_AvgNum_IHigh_AVGD.csv  | csv file containing the data for the error plot on IHigh measure               |
| TestName_AvgNum_IHigh_AVGD_A.png | png file containing a graph of the absolute error on IHigh measure             |
| TestName_AvgNum_IHigh_AVGD_R.svg | svg file containing a graph of the relative error on IHigh measure             |
|   TestName_AvgNum_ILow_AVGD.csv  | csv file containing the data for the error plot on ILow measure                |
|  TestName_AvgNum_ILow_AVGD_A.png | png file containing a graph of the absolute error on ILow measure              |
|  TestName_AvgNum_ILow_AVGD_R.svg | svg file containing a graph of the relative error on ILow measure              |
|  TestName_AvgNum_VHigh_AVGD.csv  | csv file containing the data for the error plot on VHigh measure               |
| TestName_AvgNum_VHigh_AVGD_A.png | png file containing a graph of the absolute error on VHigh measure             |
| TestName_AvgNum_VHigh_AVGD_R.svg | svg file containing a graph of the relative error on VHigh measure             |
|   TestName_AvgNum_VLow_AVGD.csv  | csv file containing the data for the error plot on VLow measure                |
|  TestName_AvgNum_VLow_AVGD_A.png | png file containing a graph of the absolute error on VLow measure              |
|  TestName_AvgNum_VLow_AVGD_R.svg | svg file containing a graph of the relative error on VLow measure              |                                            |

"""

markdown_test_coefficients="""

This script is intended to compute the calibration coefficients.

### Explanation of the test

The `GetCoefficients` test performs the calibration of certain measurement instruments used for electrical measurements (voltages and currents). The test aims to obtain calibration coefficients (gain and offset) for each instrument, which allows correcting the measurements and obtaining more accurate results.

The test establishes connections with several Digital Multimeters (DMMs) and a programmable power supply. It also interacts with communication devices (serial ports) to communicate with some instruments. Once the connections are established, the test conducts a series of measurements using different instruments for different electrical parameters (high and low voltages and currents). 
The idea is to vary each of the parameters one by one and then compare the measurements made by the TWIST with those of the DMMs. Therefore, it is possible to deduce the gain and offset that connects the TWIST measurements with those of the DMMs for each parameter.
Subsequently, it uses the obtained measurements to calculate the calibration coefficients specific to each instrument.

The calibration coefficients are stored in CSV files for future use. These coefficients are crucial to achieving accurate and consistent measurements throughout the testing and measurement process. The test concludes by deactivating the instruments and resetting certain parameters to prepare the system for other tests or tasks.

### Custom test

To run this test, you need to choose the parameters you want to apply.
- The number of samples read per duty (DMM and SPIN) for coefficients test. 
The larger the number of points, the more accurate the calibration coefficients will be. However, this will extend the test duration.
- You can also set the duty cycle and the current drawn on the low side for the VHigh, IHigh, and ILow calibrations.
- For the VLow calibration, you can fix the current drawn on low side and the VHigh value. 
During this calibration, the value of VHigh will remain at the one you have set, and the duty cycle will vary, causing VLow to change accordingly.
- Enventually, you can also manipulate the values that VHigh will take for its calibration, as well as the values that ILow will take for its calibration and the calibation of IHigh.

### Output

The script generates its output in the folder 'Output_Coefficients' created in a folder named as you named your test (this folder will be created in the folder Results).

The test generates a csv containing the calibration coefficients (gain and offset) for each quantity measured by the TWIST.
"""

markdown_test_histogram="""

This script is intended to create an histogram from a great number of measures.

### Explanation of the test

The idea behind the histogram test is to operate the system at various operating points and conduct a large number of measurements for all the parameters that the TWIST can measure. 
By gathering a significant amount of data, we can create histograms for each parameter. 
Subsequently, it will be valuable to analyze the mean and standard deviation of each parameter to evaluate the accuracy of the TWIST.

### Custom test

To run this test, you need to choose the parameters you want to apply. 

- You can set the number of samples to be read per duty cycle (DMM and SPIN). The larger the number of points, the more accurate the resulting histogram will be. However, this will extend the test duration.
- You can also adjust the duty cycle for the VHigh measurements and the current sink by the load for the VHigh measures.
By increasing these parameters, you will increase the voltage and current across the LEGs.
- Enventully, you can choose the voltage values at which you want to take your measurements. However, please note that increasing the number of data points will significantly extend the duration of your test.

### Output folder structure
The script generates output in the folder 'Output_Histogram' created in a folder named as you named your test (this folder will be created in the folder Results).
"""

markdown_DMM_address_info="""
All the DMM should be configured in SCPI communication mode. To do so, go to front panel and type the buttons : 

Shift -> GPIB -> GPIB -> ON 
Shift -> GPIB -> LANG -> SCPI

You can configure which DMM measures which parameter below. DMM addresses are specified on them.
"""

markdown_test_information="""
The scripts are developped to run under windows 10.
Other windows distributions have not been tested.

## Setup
The setup is identical for all the characterization.

### Setup : instruments
One power supply, four DMMs (Digital MultiMeter), one active load and one STLINKV3 debugger are used in the setup.

#### Setting the operating point
 - Power supply : 1 EA-PSI-9750-06
 - Active load : 1 ITECH IT8512B and a RS232 to USB interface B&K IT-E132
 - Debugger : 1 STLINKV3
note : on the actual version auto-detection of COM PORT is disabled. So for proper work, please set the correct COM Port of each instrument in the Settings.py file. Information can be found in "Ports" section of device manager of windows

#### Measuring input and output voltages and currents
 - Digital Multimeters : 4 KEITHLEY K2000 and a GPIB Interface KEYSIGHT 82357A
 - Current sensing : 2 15FR010E 5W, 10mOhm +/- 1% precision current sensing resistor
"""

markdown_info_global_parameters="""
## Global parameters

Indeed, while many parameters can be customized for each individual test, some parameters are global and will have an impact on multiple tests.
Therefore, it's essential to carefully consider and configure these global parameters to ensure consistency and meaningful comparisons across different tests. 

The global parameters you can control during the configuration of your tests include:

- You can first influence the maximum current that the load will accept to sink and the maximum power that the load will accept to sink. 
These parameters are specific to the active load you will use for your tests. It is essential to choose them carefully to ensure that your equipment is not damaged during the testing process.
By setting appropriate limits for the load's current and power sinking capabilities, you can safeguard your equipment from exceeding safe operating conditions and prevent any potential damage or risks during the testing phase. 
It is crucial to consider the specifications and ratings of your load and configure these parameters within safe and acceptable ranges to conduct reliable and secure tests.

- Next, you can fix the number of samples read per duty cycle. 
This parameter determines how many data points are collected during each duty cycle, which affects the accuracy and resolution of the tests.

- Finally, you can fix the step of the duty cycle and the starting duty cycle. 
It's important to note that if you change these parameters, you will need to modify the "main" code in the core folder and then flash the card with the updated configuration.
"""