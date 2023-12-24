This readme file is meant to give a short introduction to the content of the files in this download along with a brief intro
to using the app

There are 4 python code files include in the download:
bk8500.py - this is a python module implementing most control commands for the BK Precision 8500 series of electronic loads.
	The commands follow the information given in the 8500 manual version: 100814, with the exception of the commands nested
	under "Calibration" group which weren't implemented in this module
example.py - this is simple example code that uses the functions inside of bk8500.py. When using it make sure you modify the
	COM port parameters at the beggining of the file according to your setup. This file doesn't use every single command and
	option that was implemented in bk8500.py, but does include a vast portion of these
app.py - this is a complete control code (with basic GUI using tkinter) which is using bk8500.py to communiate with the
	instrument
app_info.py - used by app.py includes mostly static configurations as well as a few additional supporting functions

Using the control app (app.py):
The GUI is split into 3 main sections:
1 - Instrument Monitor
2 - Config/Control tabs
3 - Command log

1 - Instrument monitor:
	- Will become active once the instrument is connected. It will display the current selected mode (CC/CV/CW/CR) for
	normal operation, for "Transient" operation it will display (TR-CC/TR-CV/TR-CW/TR-CR), and for a simulated short
	operation it will display (Short).
	- The input can be turned on/off via the Enable/Disable Input button.
	- Status "lights" will display the instrument status such. This includes over-current/voltage/power/temp and reverse-
	polarity input voltage detection

2 - The central portion is split into 2 main tabs: Config/Control.
	Config:
		- "COM settings" to connect to the instrument. Please note this section includes a box to insert the instrument
		address as defined in the instrument settings. The default value is '0' in app.py as is the	case for the 8500
		instrument
		- "Instrument information" frame which will update with the instrument model/version/serial number once	connected.
		"Absolute maximum ratings" reading is derived from the model, and not read from the instrument 
		- "Instrument Configuration" can be used to control the configuration for remote sensing, enabling/disabling control
		override from the front panel of the instrument, and selection of the trigger source. Limits (voltage/current/power)
		can also be set from this frame. Note that the 8500 series has no ability to directly control the voltage/current
		range via remote control, only from the front panel. However, if you modify the appropriate limit value to a value
		that is within the lower range it will change the instrument reading range accordingly. For example, for the 8500
		setting the voltage limit to 18.0 V or lower will switch the instrument to a lower range and will proide with one
		more digit after the decimal point
		- "Instrument config store/recall" allows storing or recalling the instrument configration to one of 25 slots for
		future use. This uses the instruments internal storage, therefore can also be used from the front panel
	Control:
		- "Mode selection" includes 2 sub frames:
			- "Mode" is used to set the desired mode to CC/CV/CW/CR
			- "Function" controls the current function used:
				- Fixed for static operation with user defined values until programmed otherwise
				- Transient for switching between 2 different values, the "Mode" selected will be the one used for the
				Transient function as well as Fixed function
				- Short is meant to simulate a short across the input
			Note that 2 additional functions the instrument supports aren't included here:
				- Battery function is quite limited in the 8500 as it only support "CC" mode, and doesn't allow readback of
				the resulting capacity (AH) via remote control. This is therefore implemented differently as will be
				described later in the "Capacity meter" section
				- List function which support up to 1000 pre-defined steps. The list commands are implemented in bk8500.py
				module included in this download, but the app.py GUI doesn't include a tab that uses these commands. This
				might be added in the future
		- "Set C/V/W/R" allows setting desired value for these parameters.
		- "Capacity meter" is a somewhat more capable method of measuring capacity compared with the instruments internal
		"battery" function, but it does have some limitations. The capacity meter is implemented in app by accumulating
		the AH and WH values read from the instrument. This will continuously accumulate the values, even if the mode/function
		is changed or the output is turned off for some time. This gives quite a bit of flexibility.
		To reset the integration simply press the "reset" button.
		Since the instrument reading is only read ~2 times per second, the app has no ability to track changes which are
		shorter than that. Therefore, if for example a transient of 10ms will occour in	between samples, the instrument will
		not report this to the app and the app will assume the costant was constant for the entire duration between the
		previous readout and the current readout.
		Due to the lack of "VOLTAGE ON SET" and "VOLTAGE OFF SET" setting command in the 8500 series, theres no ability to
		limit the discharge voltage using this option without operating via front panel. Therefore, a software "Vmin" limit
		is available. If enabled, this will turn the load off once the readout voltage drops below the last set Vmin value.
		Vmin is included in the "Capacity meter" frame mostly for convinience as its most likely to be used for battery
		capacity measurements. However, it can obviously be used for other use cases too.
		- "Transient Parameters" is where you can set the 2 values (I/V/W/R) and their duration, as well as the mode of
		Transient operation. "Continuous" will continuously switch between these 2 states after the defined time has passed.
		"Pulse" will stay at value1 until a trigger is detected, at which point it will switch to value2 for the defined
		time for T2. "Toggle" will switch states when a trigger is detected. The "Trigger" button is used to send a "BUS"
		trigger to control the "Pulse"/"Toggle" modes. Note that "trigger source" must be set to "BUS" in the Config menu
		for the instrument to respond to this trigger source
		- "Load Timer" uses the instruments internal timer to limit the maximum continuous on time of the load input
3 - The bottom frame is the Command Log which will present messages as commands are implemented in response to user inputs