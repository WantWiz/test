/*
 * Copyright (c) 2021 LAAS-CNRS
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU Lesser General Public License as published by
 *   the Free Software Foundation, either version 2.1 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU Lesser General Public License for more details.
 *
 *   You should have received a copy of the GNU Lesser General Public License
 *   along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 * SPDX-License-Identifier: LGLPV2.1
 */

/**
 *  @brief   This file it the main entry point of the
 *          OwnTech Power API. Please check the README.md
 *          file at the root of this project for basic
 *          information on how to use the Power API,
 *          or refer the the wiki for detailed information.
 *          Wiki: https://gitlab.laas.fr/owntech/power-api/core/-/wikis/home
 *
 * @author  Clément Foucher <clement.foucher@laas.fr>
 */

//-------------OWNTECH DRIVERS-------------------
#include "HardwareConfiguration.h"
#include "DataAcquisition.h"
#include "Scheduling.h"
#include <stdlib.h>

//------------ZEPHYR DRIVERS----------------------
#include "zephyr.h"
#include "console/console.h"
#include "kernel.h"
include "GpioApi.h"


#define APPLICATION_THREAD_PRIORITY 5
#define COMMUNICATION_THREAD_PRIORITY 3



//--------------SETUP FUNCTIONS DECLARATION-------------------
void setup_hardware(); // setups the hardware peripherals of the system
void setup_software(); // setups the scheduling of the software and the control method

//-------------LOOP FUNCTIONS DECLARATION----------------------
void loop_communication_task(); // code to be executed in the slow communication task
int8_t CommTask_num;            // Communication Task number
void loop_application_task();   // code to be executed in the fast application task
int8_t AppTask_num;             // Application Task number
void loop_control_task();       // code to be executed in real-time at 20kHz

//--------------USER VARIABLES DECLARATIONS----------------------
static int serial_refresh_rate_ms=5;

static uint32_t control_task_period = 100; //[us] period of the control task

//Maximum figure count for duty cycle
static const uint8_t MaxCharInDuty = 20;

/* Measure variables */
static float32_t V1_low_value_converted; //store value of V1_low (app task)
static float32_t V2_low_value_converted; //store value of V2_low (app task)
static float32_t Vhigh_value_converted; //store value of Vhigh (app task)

static float32_t i1_low_value_converted; //store value of i1_low (app task)
static float32_t i2_low_value_converted; //store value of i2_low (app task)
static float32_t ihigh_value_converted; //store value of ihigh (app task)

static bool pwm_enable = false;            //[bool] state of the PWM (ctrl task)

static float meas_data; // temp storage meas value (ctrl task)

static float32_t starting_duty_cycle = 0.05;
static float32_t duty_cycle = starting_duty_cycle; //[-] duty cycle (comm task)

static float32_t duty_cycle_step = 0.05; //[-] duty cycle step (comm task)
static float32_t duty_cycle_max = 0.85; //[-] duty cycle max (control task)
static float32_t duty_cycle_min = 0.05; //[-] duty cycle min (control task)

//---------------------------------------------------------------

enum serial_interface_menu_mode // LIST OF POSSIBLE MODES FOR THE OWNTECH CONVERTER
{
    IDLEMODE = 0,
    SERIALMODE,
    POWERMODE,
    BOOSTMODE,
    BUCKMODE,
    INVERTERMODE,
};

uint8_t mode = IDLEMODE;

//---------------USER FUNCTIONS----------------------------------

float32_t update_duty_step()
{

	uint8_t carcount;
    uint8_t Hundred = 100;
	char received_char;
	char line[MaxCharInDuty];//number of character in one line
    float32_t NewDutyStep;
	float32_t NewDutyStep_Percent;

	do
	{
		//Initializing variables for eventual loop
		carcount = 0;

		printk("Enter the new duty step IN PERCENT and press enter \n");

		do
		{
			received_char = console_getchar();
			line[carcount] = received_char; 

			if(received_char == 0x08)//backspace character
			{
				if(carcount>0)//To avoid carcount being negative
					carcount--;
			}
			else
			{	
				carcount++;
			}

			printk("%c", received_char);//echoing value

			if(carcount>=(MaxCharInDuty-1))
			{
				printk("Maximum caracter allowed reached \n");
				break;
			}

		} while ((received_char!='\n')); // EOL char : CRLF
		line[carcount-2] = '\0'; // adding end of tab character to prepare for atof function

		// printk("New duty cycle step will be : %s\n", line);

		//Converting string to float
		NewDutyStep_Percent = atof(line);

		//Getting confirmation
		printk("New duty cycle step (percent) will be : %f\n", NewDutyStep_Percent);

		//Getting validation
		printk("Press y to validate, any other character to retype the duty step \n", NewDutyStep_Percent);
		received_char = console_getchar();

	}while(received_char != 'y');

    NewDutyStep = NewDutyStep_Percent/Hundred;

	return NewDutyStep;
}

//---------------SETUP FUNCTIONS----------------------------------

void setup_hardware()
{
    dataAcquisition.configureAdcDefaultAllMeasurements();
    // dataAcquisition.getCalibrationFactors();
    console_init();
    hwConfig.setBoardVersion(SPIN_v_0_9);
    hwConfig.initInterleavedBuckMode(); // initialize in buck mode
    // hwConfig.initInterleavedBoostMode(); // initialize in boost mode
    // hwConfig.setLedOn();
    gpio.configurePin(PC6, OUTPUT);
    gpio.setPin(PC6);//To set HIGH (activate NGND)
}


void setup_software()
{   

    // For mA and mV results
    dataAcquisition.setV1LowParameters(45.021,-94364);
    dataAcquisition.setV2LowParameters(45.021,-94364);
    dataAcquisition.setVHighParameters(67.426,0);
    dataAcquisition.setI1LowParameters(5,-10000);
    dataAcquisition.setI2LowParameters(5,-10000);
    dataAcquisition.setIHighParameters(5,-10000);

    // For A and V results
    // dataAcquisition.setParameters(V1_LOW, 0.045, -94.364);
    // dataAcquisition.setParameters(V2_LOW, 0.045, -94.364);
    // dataAcquisition.setParameters(V_HIGH, 0.0674, 0);
    // dataAcquisition.setParameters(I1_LOW, 0.005, -10);
    // dataAcquisition.setParameters(I2_LOW, 0.005, -10);
    // dataAcquisition.setParameters(I_HIGH, 0.005, -10);

    dataAcquisition.start();

    AppTask_num = scheduling.defineAsynchronousTask(loop_application_task);
    CommTask_num = scheduling.defineAsynchronousTask(loop_communication_task);

    scheduling.defineUninterruptibleSynchronousTask(&loop_control_task, control_task_period);
    scheduling.startAsynchronousTask(AppTask_num);
    scheduling.startAsynchronousTask(CommTask_num);
    scheduling.startUninterruptibleSynchronousTask();

    // scheduling.startCommunicationTask(loop_communication_task,COMMUNICATION_THREAD_PRIORITY);
    // scheduling.startApplicationTask(loop_application_task,APPLICATION_THREAD_PRIORITY);
}

//---------------LOOP FUNCTIONS----------------------------------

void loop_communication_task()
{
    while (1)
    {
        
        uint8_t received_char = console_getchar();

        switch (received_char) {
        {
        case 'h':
            //----------SERIAL INTERFACE MENU-----------------------
            printk(" ________________________________________\n");
            printk("|     ------- MENU ---------             |\n");
            printk("|     press i : idle mode                |\n");
            printk("|     press s : serial mode              |\n");
            printk("|     press p : power mode               |\n");
            printk("|     press u : duty cycle UP            |\n");
            printk("|     press d : duty cycle DOWN          |\n");
            printk("|     press k : Calibration              |\n");
            printk("|     press t : Default coeffs           |\n");
            printk("|     press x : set duty step            |\n");
            printk("|________________________________________|\n");
            //------------------------------------------------------
            break;
        case 'i':
            mode = IDLEMODE;
            break;
        case 's':
            // printk("serial mode\n");
            mode = SERIALMODE;
            break;
        case 'p':
            mode = POWERMODE;
            break;
        case 'u':
            duty_cycle = duty_cycle + duty_cycle_step;
            if(duty_cycle>=duty_cycle_max) duty_cycle = duty_cycle_max;
            break;
        case 'd':
            duty_cycle = duty_cycle - duty_cycle_step;
            if(duty_cycle<=duty_cycle_min) duty_cycle = duty_cycle_min;
            break;
        case 'r':
            duty_cycle = starting_duty_cycle;
            break;
        case 'k':
            mode = IDLEMODE;
            dataAcquisition.setUserCalibrationFactors();
            break;
        case 't':
            dataAcquisition.setDefaultCalibrationFactors();
            break;
        case 'x':
            mode = IDLEMODE;
            duty_cycle_step = update_duty_step();
            printk("Applied duty step will be: %f", duty_cycle_step);
            break;
        default:
            printk("%c", received_char);
            break;
            }
        }
    }
}

void loop_application_task()
{   
    u_int8_t led_status=0;

    while (1)
    {
        if (mode == IDLEMODE)
        {   
            if(led_status == 1)
            {
                hwConfig.setLedOff();
                led_status = 0;
            }
        }

        else if(mode==SERIALMODE) 
        {
            if(led_status == 1)
            {
                hwConfig.setLedOff();
                led_status = 0;
            }

            printk("%.2f:", duty_cycle);
            printk("%.0f:", Vhigh_value_converted);
            printk("%.0f:", V1_low_value_converted);
            printk("%.0f:", V2_low_value_converted);
            printk("%.0f:", ihigh_value_converted);
            printk("%.0f:", i1_low_value_converted);
            printk("%.0f\n", i2_low_value_converted);
        }
        
        else if(mode==POWERMODE) 
        {
            if(led_status == 0)
            {
                hwConfig.setLedOn();
                led_status = 1;
            }
            printk("%.2f:", duty_cycle);
            printk("%.0f:", Vhigh_value_converted);
            printk("%.0f:", V1_low_value_converted);
            printk("%.0f:", V2_low_value_converted);
            printk("%.0f:", ihigh_value_converted);
            printk("%.0f:", i1_low_value_converted);
            printk("%.0f\n", i2_low_value_converted);
        }
        scheduling.suspendCurrentTaskMs(serial_refresh_rate_ms);
    }
}

void loop_control_task()
{
    meas_data = dataAcquisition.getVHigh();
    if(meas_data!=-10000) Vhigh_value_converted = meas_data;

    meas_data = dataAcquisition.getV1Low();
    if(meas_data!=-10000) V1_low_value_converted = meas_data;

    meas_data = dataAcquisition.getV2Low();
    if(meas_data!=-10000) V2_low_value_converted= meas_data;

    meas_data = dataAcquisition.getIHigh();
    if(meas_data!=-10000) ihigh_value_converted = meas_data;

    meas_data = dataAcquisition.getI1Low();
    if(meas_data!=-10000) i1_low_value_converted = meas_data;

    meas_data = dataAcquisition.getI2Low();
    if(meas_data!=-10000) i2_low_value_converted = meas_data;

    if(mode==IDLEMODE || mode==SERIALMODE) {
        pwm_enable = false;
        hwConfig.setInterleavedOff();

    }else if(mode==POWERMODE || mode==BOOSTMODE || mode == BUCKMODE || mode == INVERTERMODE) {

        if(!pwm_enable) {
            pwm_enable = true;
            hwConfig.setInterleavedOn();
        }

        if(mode==POWERMODE)
        {   
            hwConfig.setInterleavedDutyCycle(duty_cycle);
            hwConfig.setHrtimAdcTrigInterleaved(0.1*duty_cycle+(duty_cycle/2));
        }
    }
}

/**
 * This is the main function of this example
 * This function is generic and does not need editing.
 */
void main(void)
{
    setup_hardware();
    setup_software();
}
