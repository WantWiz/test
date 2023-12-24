# bk8500 series controler, app.py version 1.0 , downloaded from: www.TolisDIY.com
# Controller was tested on a BK Precision 8500 (120V/30A/300W) instrument on a Window machine

import contextlib
import io
import serial
import glob
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import time
from app_info import *
import bk8500

ser = serial.Serial()
port = ""
baud = 9600
parity = "N"
address = 0
inst_busy = False
inst_queue = ""
timeout = 2
model = ""
version = ""
serial_number = ""
connected = False
cap_ah = float(0)
cap_wh = float(0)
vmin = float(0)
vlim = float(0)
update_prd = 0.5
instrument_state = ""
fixed_mode = 1
dt = time.time()

opt_ser_ports = serial_ports()

def queue_handler():
    global inst_queue
    temp = inst_queue
    if temp == "com_end":
        com_end()
    elif temp[0:7] == "rem_sen":
        if temp[8] == "T":
            remote_sense(True)
        else:
            remote_sense(False)
    elif temp[0:7] == "loc_str":
        if temp[8] == "T":
            local_bypass(True)
        else:
            local_bypass(False)
    elif temp[0:7] == "trg_src":
        trig_source(int(temp[8]))
    elif temp == "set_lim":
        set_max_vals()
    elif temp[0:7] == "mod_set":
        mode_change(int(temp[8]))
    elif temp[0:7] == "spe_mod":
        spec_mode_change(int(temp[8]))
    elif temp == "val_set":
        set_vals()
    elif temp == "inp_cha":
        input_change()
    elif temp == "trn_set":
        tran_set()
    elif temp == "trn_trg":
        tran_trig()
    elif temp == "tim_set":
        timer_val_set()
    elif temp[0:7] == "tim_ena":
        if temp[8] == "T":
            timer_enable(True)
        else:
            timer_enable(False)
    elif temp == "str_set":
        store_settings()
    elif temp == "rcl_set":
        recall_settings()
    else:
        pass
    inst_queue = ""

def com_port_change(event):
    global port
    port = var_opt_ports.get()

def com_baud_change(event):
    global baud
    baud = int(var_opt_baud.get())

def com_parity_change(event):
    global parity
    temp = var_opt_parity.get()
    if temp == "none":
        parity = 'N'
    elif temp == "even":
        parity = 'E'
    else:
        parity = 'O'

def com_end():
    global connected
    global address
    print("Disconnecting from instrument\n")
    # unset remote
    io_string = io.StringIO()
    with contextlib.redirect_stdout(io_string):
        bk8500.set_remote(ser, address, False)
    log_text_box.insert("1.0", io_string.getvalue()+"\n")
    ser.close()
    label_inst_model.config(text="Model: ")
    label_inst_ver.config(text="Version: ")
    label_inst_sn.config(text="Serial Number: ")
    label_inst_max_rat.config(text="Absolute Maximum Ratings:")
    entry_maxv.delete(0, END)
    entry_maxi.delete(0, END)
    entry_maxw.delete(0, END)
    entry_seti.delete(0,END)
    entry_setv.delete(0, END)
    entry_setw.delete(0, END)
    entry_setr.delete(0, END)
    entry_tran_val1.delete(0,END)
    entry_tran_time1.delete(0, END)
    entry_tran_val2.delete(0, END)
    entry_tran_time2.delete(0, END)
    label_mon_mode2.config(text = "")
    label_mon_volt2.config(text="")
    label_mon_cur2.config(text="")
    label_mon_pow2.config(text="")
    status_canvas.itemconfig(status_light2, fill="gray")
    print("Instrument disconnected\n")
    connected = False
    # change button
    com_connect_button.config(text="Connect")

def com_button_click(event):
    global t
    global dt
    global address
    global inst_queue
    global inst_busy
    global connected
    global update_prd
    if connected:
        if inst_busy:
            inst_queue = "com_end"
        else:
            inst_busy = True
            com_end()
            inst_busy = False
    else:
        if int(win_ser_addr.get())<255 and int(win_ser_addr.get())>=0:
            address = int(win_ser_addr.get())
        ser.baudrate = baud
        ser.parity = parity
        ser.timeout = timeout
        print("Trying to connect to instrument\n")
        if len(port)>0:
            ser.port = port
            ser.open()
        else:
            print("Check selected port\n")
        if ser.is_open:
            print("Serial connection open\n")
            # set remote
            io_string = io.StringIO()
            with contextlib.redirect_stdout(io_string):
                bk8500.set_remote(ser, address, True)
            log_text_box.insert("1.0", io_string.getvalue()+"\n")
            # get instrument info
            io_string = io.StringIO()
            with contextlib.redirect_stdout(io_string):
                response = bk8500.get_product_info(ser, address)
            log_text_box.insert("1.0", io_string.getvalue()+"\n")
            #update GUI with device info
            label_inst_model.config(text="Model: "+response[0])
            label_inst_ver.config(text="Version: "+response[1])
            label_inst_sn.config(text="Serial Number: "+response[2])
            label_inst_max_rat.config(text="Absolute Maximum Ratings: "+Models_list[response[0]])
            #change button
            com_connect_button.config(text = "Disconnect")
            #get all info and update panel accordingly
            print("Getting current instrument configuration\n")
            io_string = io.StringIO()
            with contextlib.redirect_stdout(io_string):
                response = bk8500.get_remote_sense(ser,address)
            log_text_box.insert("1.0", io_string.getvalue()+"\n")
            if response:
                remote_sense_var.set(True)
            else:
                remote_sense_var.set(False)
            io_string = io.StringIO()
            with contextlib.redirect_stdout(io_string):
                response = bk8500.get_trig_source(ser,address)
            log_text_box.insert("1.0", io_string.getvalue()+"\n")
            if response=="IMMEDIATE":
                trig_src_var.set("1")
            elif response=="EXTERNAL":
                trig_src_var.set("2")
            else:
                trig_src_var.set("3")
            update_limits()
            update_mode()
            update_spec_mode()
            update_vals()
            status_update()
            tran_get()
            timer_update()
            connected = True
            dt = time.time()
            t.start()
        else:
            print("Unable to open serial port\n")

def remote_sense(value):
    global address
    io_string = io.StringIO()
    with contextlib.redirect_stdout(io_string):
        bk8500.set_remote_sense(ser, address, value)
    log_text_box.insert("1.0", io_string.getvalue()+"\n")

def remote_sense_click():
    global inst_busy
    global inst_queue
    global connected
    if connected:
        if inst_busy:
            if (remote_sense_var.get()):
                inst_queue = "rem_sen=T"
            else:
                inst_queue = "rem_sen=F"
        else:
            inst_busy = True
            remote_sense(remote_sense_var.get())
            queue_handler()
            inst_busy = False
    else:
        pass

def local_bypass(value):
    global address
    io_string = io.StringIO()
    with contextlib.redirect_stdout(io_string):
        bk8500.set_local_control_bypass(ser, address, value)
    log_text_box.insert("1.0", io_string.getvalue()+"\n")

def local_ctrl_click():
    global inst_busy
    global inst_queue
    global connected
    if connected:
        if inst_busy:
            if (remote_sense_var.get()):
                inst_queue = "loc_ctr=T"
            else:
                inst_queue = "loc_ctr=F"
        else:
            inst_busy = True
            local_bypass(local_ctrl_var.get())
            queue_handler()
            inst_busy = False
    else:
        pass

def trig_source(value):
    global address
    io_string = io.StringIO()
    if (value == 1):
        mode = "IMM"
    elif (value == 2):
        mode = "EXT"
    else:
        mode = "BUS"
    with contextlib.redirect_stdout(io_string):
        bk8500.set_trig_source(ser, address, mode)
    log_text_box.insert("1.0", io_string.getvalue()+"\n")

def trig_src_click():
    global inst_busy
    global inst_queue
    global connected
    if connected:
        if inst_busy:
            if (trig_src_var.get() == 1):
                inst_queue = "trg_src=1"
            elif (trig_src_var.get() == 2):
                inst_queue = "trg_src=2"
            else:
                inst_queue = "trg_src=3"
        else:
            inst_busy = True
            trig_source(trig_src_var.get())
            queue_handler()
            inst_busy = False
    else:
        pass

def update_limits():
    global vlim
    global address
    entry_maxv.delete(0, END)
    io_string = io.StringIO()
    with contextlib.redirect_stdout(io_string):
        response = bk8500.get_max_voltage(ser, address)
    log_text_box.insert("1.0", io_string.getvalue() + "\n")
    entry_maxv.insert(0, str(response))
    vlim=response
    entry_maxi.delete(0, END)
    io_string = io.StringIO()
    with contextlib.redirect_stdout(io_string):
        response = bk8500.get_max_current(ser, address)
    log_text_box.insert("1.0", io_string.getvalue() + "\n")
    entry_maxi.insert(0, str(response))
    entry_maxw.delete(0, END)
    io_string = io.StringIO()
    with contextlib.redirect_stdout(io_string):
        response = bk8500.get_max_power(ser, address)
    log_text_box.insert("1.0", io_string.getvalue() + "\n")
    entry_maxw.insert(0, str(response))
    update_vals()

def set_max_vals():
    global address
    try:
        io_string = io.StringIO()
        with contextlib.redirect_stdout(io_string):
            bk8500.set_max_voltage(ser, address, float(entry_maxv.get()))
        log_text_box.insert("1.0", io_string.getvalue()+"\n")
        io_string = io.StringIO()
        with contextlib.redirect_stdout(io_string):
            bk8500.set_max_current(ser, address, float(entry_maxi.get()))
        log_text_box.insert("1.0", io_string.getvalue()+"\n")
        io_string = io.StringIO()
        with contextlib.redirect_stdout(io_string):
            bk8500.set_max_power(ser, address, float(entry_maxw.get()))
        log_text_box.insert("1.0", io_string.getvalue()+"\n")
        update_limits()
    except:
        print("Check values of chosen limits\n")

def max_set_button_click(event):
    global inst_busy
    global inst_queue
    global connected
    if connected:
        if inst_busy:
            inst_queue = "set_lim"
        else:
            inst_busy = True
            set_max_vals()
            queue_handler()
            inst_busy = False
    else:
        pass

def store_settings():
    global address
    io_string = io.StringIO()
    with contextlib.redirect_stdout(io_string):
        bk8500.store_settings(ser, address, var_opt_setting_slot.get())
    log_text_box.insert("1.0", io_string.getvalue() + "\n")

def store_settings_click(event):
    global inst_busy
    global inst_queue
    global connected
    if connected:
        if inst_busy:
            inst_queue = "str_set"
        else:
            inst_busy = True
            store_settings()
            queue_handler()
            inst_busy = False
    else:
        pass

def recall_settings():
    global address
    io_string = io.StringIO()
    with contextlib.redirect_stdout(io_string):
        bk8500.recall_settings(ser, address, var_opt_setting_slot.get())
        bk8500.get_remote_sense(ser, address)
        bk8500.get_trig_source(ser, address)
        update_limits()
        update_mode()
        update_spec_mode()
        update_vals()
        status_update()
        tran_get()
        timer_update()
    log_text_box.insert("1.0", io_string.getvalue() + "\n")

def recall_settings_click(event):
    global inst_busy
    global inst_queue
    global connected
    if connected:
        if inst_busy:
            inst_queue = "rcl_set"
        else:
            inst_busy = True
            recall_settings()
            queue_handler()
            inst_busy = False
    else:
        pass

def update_mode():
    global fixed_mode
    global address
    io_string = io.StringIO()
    with contextlib.redirect_stdout(io_string):
        response = bk8500.get_mode(ser, address)
    log_text_box.insert("1.0", io_string.getvalue() + "\n")
    if response == "CC":
        mode_var.set(1)
        fixed_mode = 1
        label_mon_mode2.config(text="CC")
    elif response == "CV":
        mode_var.set(2)
        fixed_mode = 2
        label_mon_mode2.config(text="CV")
    elif response == "CW":
        mode_var.set(3)
        fixed_mode = 3
        label_mon_mode2.config(text="CW")
    elif response == "CR":
        mode_var.set(4)
        fixed_mode = 4
        label_mon_mode2.config(text="CR")
    else:
        pass

def mode_change(value):
    global address
    mode = 0
    io_string = io.StringIO()
    if (value == 1):
        mode = "CC"
    elif (value == 2):
        mode = "CV"
    elif (value == 3):
        mode = "CW"
    elif (value == 4):
        mode = "CR"
    if spec_mode_var.get() == 2:  #if in transient mode, move to fixed first, then back to transient
        bk8500.set_function(ser,address,"FIXED")
    with contextlib.redirect_stdout(io_string):
        bk8500.set_mode(ser, address, mode)
    log_text_box.insert("1.0", io_string.getvalue()+"\n")
    if spec_mode_var.get() == 2:  #if in transient mode, move to fixed first, then back to transient
        bk8500.set_function(ser,address,"TRANSIENT")
    update_mode()
    update_spec_mode()
    tran_get()

def mode_click():
    global inst_busy
    global inst_queue
    global connected
    if connected:
        temp = mode_var.get()
        if inst_busy:
            inst_queue = "mod_set=" + str(temp)
        else:
            inst_busy = True
            mode_change(temp)
            queue_handler()
            inst_busy = False
    else:
        pass

def update_spec_mode():
    global address
    io_string = io.StringIO()
    with contextlib.redirect_stdout(io_string):
        response = bk8500.get_function(ser, address)
    log_text_box.insert("1.0", io_string.getvalue() + "\n")
    temp = bk8500.get_mode(ser,address)
    if response == 0:
        spec_mode_var.set(1)
        label_mon_mode2.config(text=temp)
    elif response == 1:
        spec_mode_var.set(3)
        label_mon_mode2.config(text="SHORT")
        mode_var.set(0)
    elif response == 2:
        spec_mode_var.set(2)
        label_mon_mode2.config(text="TR-" + temp)
    else:
        spec_mode_var.set(0)

def spec_mode_change(value):
    global address
    io_string = io.StringIO()
    if value == 1:
        with contextlib.redirect_stdout(io_string):
            bk8500.set_function(ser,address,"FIXED")
        log_text_box.insert("1.0", io_string.getvalue()+"\n")
        update_mode()
    elif value == 2:
        with contextlib.redirect_stdout(io_string):
            bk8500.set_function(ser,address,"TRANSIENT")
        log_text_box.insert("1.0", io_string.getvalue()+"\n")
        update_mode()
    elif value == 3:
        with contextlib.redirect_stdout(io_string):
            bk8500.set_function(ser,address,"SHORT")
        log_text_box.insert("1.0", io_string.getvalue()+"\n")
    else:
        pass
    update_spec_mode()

def spec_mode_click():
    global inst_busy
    global inst_queue
    global connected
    if connected:
        temp = spec_mode_var.get()
        if inst_busy:
            inst_queue = "spe_mod=" + str(temp)
        else:
            inst_busy = True
            spec_mode_change(temp)
            queue_handler()
            inst_busy = False
    else:
        pass

def update_vals():
    global address
    entry_seti.delete(0, END)
    io_string = io.StringIO()
    with contextlib.redirect_stdout(io_string):
        response = bk8500.get_current(ser, address)
    log_text_box.insert("1.0", io_string.getvalue() + "\n")
    entry_seti.insert(0, str(response))
    entry_setv.delete(0, END)
    io_string = io.StringIO()
    with contextlib.redirect_stdout(io_string):
        response = bk8500.get_voltage(ser, address)
    log_text_box.insert("1.0", io_string.getvalue() + "\n")
    entry_setv.insert(0, str(response))
    entry_setw.delete(0, END)
    io_string = io.StringIO()
    with contextlib.redirect_stdout(io_string):
        response = bk8500.get_power(ser, address)
    log_text_box.insert("1.0", io_string.getvalue() + "\n")
    entry_setw.insert(0, str(response))
    entry_setr.delete(0, END)
    io_string = io.StringIO()
    with contextlib.redirect_stdout(io_string):
        response = bk8500.get_resistance(ser, address)
    log_text_box.insert("1.0", io_string.getvalue() + "\n")
    entry_setr.insert(0, str(response))

def set_vals():
    global address
    try:
        io_string = io.StringIO()
        with contextlib.redirect_stdout(io_string):
            bk8500.set_current(ser, address, float(entry_seti.get()))
        log_text_box.insert("1.0", io_string.getvalue()+"\n")
        io_string = io.StringIO()
        with contextlib.redirect_stdout(io_string):
            bk8500.set_voltage(ser, address, float(entry_setv.get()))
        log_text_box.insert("1.0", io_string.getvalue()+"\n")
        io_string = io.StringIO()
        with contextlib.redirect_stdout(io_string):
            bk8500.set_power(ser, address, float(entry_setw.get()))
        log_text_box.insert("1.0", io_string.getvalue()+"\n")
        io_string = io.StringIO()
        with contextlib.redirect_stdout(io_string):
            bk8500.set_resistance(ser, address, float(entry_setr.get()))
        log_text_box.insert("1.0", io_string.getvalue() + "\n")
        update_vals()
    except:
        print("An exception occurred, check values of chosen limits\n")

def val_set_button_click(event):
    global inst_busy
    global inst_queue
    global connected
    if connected:
        if inst_busy:
            inst_queue = "val_set"
        else:
            inst_busy = True
            set_vals()
            queue_handler()
            inst_busy = False
    else:
        pass

def cap_reset_button_click(event):
    global cap_ah
    global cap_wh
    cap_ah = float(0)
    cap_wh = float(0)
    label_val_ah.config(text=str(round(cap_ah, 3)))
    label_val_wh.config(text = str(round(cap_wh, 3)))

def cap_vmin_set_click(event):
    global vmin
    try:
        temp = float(entry_cap_vmin.get())
        if temp>=0 and temp<vlim:
            vmin = temp
        else:
            print("Vmin must be in the range of 0 to Voltage Limit (" + str(vlim) + "V)\n")
        entry_cap_vmin.delete(0,END)
        entry_cap_vmin.insert(0,str(round(vmin,3)))
    except:
        print("Vmin must be in the range of 0 to aaaVoltage Limit (" + str(vlim) + "V)\n")
        entry_cap_vmin.delete(0, END)
        entry_cap_vmin.insert(0, str(round(vmin, 3)))

def status_update():
    global address
    global instrument_state
    global update_prd
    global t
    global dt
    global cap_ah
    global cap_wh
    log_text_box.delete(200.0,END)
    response = bk8500.get_instrument_state(ser,address)
    label_mon_volt2.config(text=str(round(response[0],3)))
    label_mon_cur2.config(text=str(round(response[1], 4)))
    label_mon_pow2.config(text=str(round(response[2], 3)))
    temp = time.time()
    cap_ah = cap_ah + (temp-dt)*response[1]/3600
    cap_wh = cap_wh + (temp-dt)*response[2]/3600
    label_val_ah.config(text=str(round(cap_ah, 3)))
    label_val_wh.config(text=str(round(cap_wh, 3)))
    dt = temp
    if response[4]:
        status_canvas.itemconfig(status_light1, fill="green")
    else:
        status_canvas.itemconfig(status_light1, fill="gray")
    if response[5]:
        status_canvas.itemconfig(status_light2, fill="green")
    else:
        status_canvas.itemconfig(status_light2, fill="gray")
    if response[6]:
        status_canvas.itemconfig(status_light3, fill="green")
    else:
        status_canvas.itemconfig(status_light3, fill="gray")
    if response[7]:
        local_ctrl_var.set(True)
    else:
        local_ctrl_var.set(False)
    if response[8]:
        status_canvas.itemconfig(status_light4, fill="green")
    else:
        status_canvas.itemconfig(status_light4, fill="gray")
    if response[9]:
        status_canvas.itemconfig(status_light5, fill="green")
    else:
        status_canvas.itemconfig(status_light5, fill="gray")
    if response[10]:
        status_canvas.itemconfig(status_light6, fill="red")
    else:
        status_canvas.itemconfig(status_light6, fill="gray")
    if response[11]:
        status_canvas.itemconfig(status_light7, fill="red")
    else:
        status_canvas.itemconfig(status_light7, fill="gray")
    if response[12]:
        status_canvas.itemconfig(status_light8, fill="red")
    else:
        status_canvas.itemconfig(status_light8, fill="gray")
    if response[13]:
        status_canvas.itemconfig(status_light9, fill="red")
    else:
        status_canvas.itemconfig(status_light9, fill="gray")
    if response[14]:
        status_canvas.itemconfig(status_light10, fill="red")
    else:
        status_canvas.itemconfig(status_light10, fill="gray")
    instrument_state = response
    if check_cap_vmin_var.get() and response[0]<vmin and instrument_state[6]:
        input_change()
        print("Voltage dropped below Vmin threshold, input has been turned off")
    else:
        pass
    if instrument_state[6]:
        input_change_button.config(text = "Disable\nInput")
    else:
        input_change_button.config(text="Enable\nInput")
    return

def timed_status_update():
    global inst_busy
    global connected
    if connected:
        if inst_busy:
            pass
        else:
            inst_busy = True
            status_update()
            queue_handler()
            inst_busy = False
        t.start()
    else:
        pass

def input_change():
    global address
    global instrument_state
    io_string = io.StringIO()
    if instrument_state[6]:
        with contextlib.redirect_stdout(io_string):
            bk8500.enable_input(ser, address, False)
        print("Disabling input\n")
    else:
        with contextlib.redirect_stdout(io_string):
            bk8500.enable_input(ser, address, True)
        print("Enabling input\n")
    status_update()

def input_change_click(event):
    global inst_busy
    global inst_queue
    global connected
    if connected:
        if inst_busy:
            inst_queue = "inp_cha"
        else:
            inst_busy = True
            input_change()
            queue_handler()
            inst_busy = False
    else:
        pass

def tran_get():
    global tran_mode
    global fixed_mode
    global address
    entry_tran_val1.delete(0, END)
    entry_tran_time1.delete(0, END)
    entry_tran_val2.delete(0, END)
    entry_tran_time2.delete(0, END)
    io_string = io.StringIO()
    temp = [0.0,0.0,0.0,0.0,"CONTINUOUS"]
    if fixed_mode == 1:
        with contextlib.redirect_stdout(io_string):
            temp = bk8500.get_tran_CC_param(ser, address)
        log_text_box.insert("1.0", io_string.getvalue() + "\n")
        label_tran_val1.config(text="I1 [A]:")
        label_tran_val2.config(text="I2 [A]:")
    elif fixed_mode == 2:
        with contextlib.redirect_stdout(io_string):
            temp = bk8500.get_tran_CV_param(ser, address)
        log_text_box.insert("1.0", io_string.getvalue() + "\n")
        label_tran_val1.config(text="V1 [V]:")
        label_tran_val2.config(text="V2 [V]:")
    elif fixed_mode == 3:
        with contextlib.redirect_stdout(io_string):
            temp = bk8500.get_tran_CW_param(ser, address)
        log_text_box.insert("1.0", io_string.getvalue() + "\n")
        label_tran_val1.config(text="P1 [W]:")
        label_tran_val2.config(text="P2 [W]:")
    elif fixed_mode == 4:
        with contextlib.redirect_stdout(io_string):
            temp = bk8500.get_tran_CR_param(ser, address)
        log_text_box.insert("1.0", io_string.getvalue() + "\n")
        label_tran_val1.config(text="R1 [Ohm]:")
        label_tran_val2.config(text="R2 [Ohm]:")
    else:
        pass
    entry_tran_val1.insert(0,str(temp[0]))
    entry_tran_time1.insert(0,str(temp[1]))
    entry_tran_val2.insert(0,str(temp[2]))
    entry_tran_time2.insert(0,str(temp[3]))
    if temp[4] == 1:
        var_tran_op.set(opt_tran_op[1])
        entry_tran_time1.config(fg='Gray',bg='LightGray')
        entry_tran_time2.config(fg='Black', bg='White')
        tran_trig_button.config(fg='Black')
    elif temp[4] == 2:
        var_tran_op.set(opt_tran_op[2])
        entry_tran_time1.config(fg='Gray', bg='LightGray')
        entry_tran_time2.config(fg='Gray', bg='LightGray')
        tran_trig_button.config(fg='Black')
    else:
        var_tran_op.set(opt_tran_op[0])
        entry_tran_time1.config(fg='Black', bg='White')
        entry_tran_time2.config(fg='Black', bg='White')
        tran_trig_button.config(fg='Gray')
    tran_mode = temp[4]

def tran_set():
    global address
    global tran_mode
    op = var_tran_op.get()
    try:
        val1 = float(entry_tran_val1.get())
        time1 = float(entry_tran_time1.get())
        val2 = float(entry_tran_val2.get())
        time2 = float(entry_tran_time2.get())
        io_string = io.StringIO()
        if spec_mode_var.get() == 2:  # if in transient mode, move to fixed first, then back to transient
            bk8500.set_function(ser, address, "FIXED")
        if fixed_mode==1:
            with contextlib.redirect_stdout(io_string):
                bk8500.set_tran_CC_param(ser,address,val1,time1,val2,time2,op)
            log_text_box.insert("1.0", io_string.getvalue() + "\n")
        elif fixed_mode==2:
            with contextlib.redirect_stdout(io_string):
                bk8500.set_tran_CV_param(ser, address, val1, time1, val2, time2, op)
            log_text_box.insert("1.0", io_string.getvalue() + "\n")
        elif fixed_mode==3:
            with contextlib.redirect_stdout(io_string):
                bk8500.set_tran_CW_param(ser, address, val1, time1, val2, time2, op)
            log_text_box.insert("1.0", io_string.getvalue() + "\n")
        elif fixed_mode==4:
            with contextlib.redirect_stdout(io_string):
                bk8500.set_tran_CR_param(ser, address, val1, time1, val2, time2, op)
            log_text_box.insert("1.0", io_string.getvalue() + "\n")
        else:
            print("Transient parameters only valid in CC/CV/CW/CR modes")
        if spec_mode_var.get() == 2:  # if in transient mode, move to fixed first, then back to transient
            bk8500.set_function(ser, address, "TRANSIENT")
    except:
        print("Check entered values for transient parameters")
    tran_get()

def tran_set_click(event):
    global inst_busy
    global inst_queue
    global connected
    if connected:
        if inst_busy:
            inst_queue = "trn_set"
        else:
            inst_busy = True
            tran_set()
            queue_handler()
            inst_busy = False
    else:
        pass

def tran_trig():
    global address
    io_string = io.StringIO()
    with contextlib.redirect_stdout(io_string):
        bk8500.trig_instrument(ser, address)
    log_text_box.insert("1.0", io_string.getvalue() + "\n")

def tran_trig_click(event):
    global inst_busy
    global inst_queue
    global connected
    if connected:
        if inst_busy:
            inst_queue = "trn_trg"
        else:
            inst_busy = True
            tran_trig()
            queue_handler()
            inst_busy = False
    else:
        pass

def timer_update():
    global address
    io_string = io.StringIO()
    with contextlib.redirect_stdout(io_string):
        if bk8500.get_load_timer_mode(ser,address):
            timer_enable_var.set(True)
        else:
            timer_enable_var.set(False)
    log_text_box.insert("1.0", io_string.getvalue() + "\n")
    io_string = io.StringIO()
    with contextlib.redirect_stdout(io_string):
        entry_timer.delete(0,END)
        entry_timer.insert(0,str(bk8500.get_load_timer_value(ser,address)))
    log_text_box.insert("1.0", io_string.getvalue() + "\n")

def timer_val_set():
    global address
    io_string = io.StringIO()
    try:
        value = int(entry_timer.get())
        with contextlib.redirect_stdout(io_string):
            bk8500.set_load_timer_value(ser,address,value)
        log_text_box.insert("1.0", io_string.getvalue() + "\n")
    except:
        print("Check entered timer value")
    timer_update()

def timer_set_click(event):
    global inst_busy
    global inst_queue
    global connected
    if connected:
        if inst_busy:
            inst_queue = "tim_set"
        else:
            inst_busy = True
            timer_val_set()
            queue_handler()
            inst_busy = False
    else:
        pass

def timer_enable(value):
    global address
    io_string = io.StringIO()
    temp = instrument_state[6]
    if temp:
        bk8500.enable_input(ser,address,False)
    with contextlib.redirect_stdout(io_string):
        bk8500.set_load_timer_mode(ser,address,value)
    log_text_box.insert("1.0", io_string.getvalue()+"\n")
    if temp:
        bk8500.enable_input(ser,address,True)
    timer_update()

def timer_enable_click():
    global inst_busy
    global inst_queue
    global connected
    if connected:
        if inst_busy:
            if timer_enable_var.get():
                inst_queue = "tim_ena=T"
            else:
                inst_queue = "tim_ena=F"
        else:
            inst_busy = True
            timer_enable(timer_enable_var.get())
            queue_handler()
            inst_busy = False
    else:
        pass


# Define window and GUI items
window = Tk()
window.option_add('*Font', 'David 12')
window.geometry("900x1200")
window.title("BK8500 Instrument Control")

style = ttk.Style(window)
style.theme_settings("vista", {"TNotebook.Tab": {"configure": {"padding": [5, 5],"font" : ('David', '12', 'bold')}}})
style.theme_use("vista")

frame_top = Frame(master=window)
frame_bot = Frame(master=window)

#Top Frame content:
top_frame_sur = ttk.LabelFrame(frame_top, text = "Instrument Monitor")
top_frame = Frame(master=top_frame_sur)

mode_top_frame = Frame(master=top_frame)
label_mon_mode1 = Label(master=mode_top_frame, text=" Mode ", width = 6)
label_mon_mode2 = Label(master=mode_top_frame, text="", width = 6, fg="black")
label_mon_mode1.config(font=("Courier New", 20))
label_mon_mode2.config(font=("Courier New", 32))
label_mon_mode1.pack()
label_mon_mode2.pack()
volt_top_frame = Frame(master=top_frame)
label_mon_volt1 = Label(master=volt_top_frame, text=" Voltage ", width = 12)
label_mon_volt2 = Label(master=volt_top_frame, text="", width = 6, fg="black")
label_mon_volt1.config(font=("Courier New", 20))
label_mon_volt2.config(font=("Courier New", 32))
label_mon_volt1.pack()
label_mon_volt2.pack()
cur_top_frame = Frame(master=top_frame)
label_mon_cur1 = Label(master=cur_top_frame, text=" Current ", width = 12)
label_mon_cur2 = Label(master=cur_top_frame, text="", width = 6, fg="black")
label_mon_cur1.config(font=("Courier New", 20))
label_mon_cur2.config(font=("Courier New", 32))
label_mon_cur1.pack()
label_mon_cur2.pack()
pow_top_frame = Frame(master=top_frame)
label_mon_pow1 = Label(master=pow_top_frame, text=" Power ", width = 12)
label_mon_pow2 = Label(master=pow_top_frame, text="", width = 6, fg="black")
label_mon_pow1.config(font=("Courier New", 20))
label_mon_pow2.config(font=("Courier New", 32))
label_mon_pow1.pack()
label_mon_pow2.pack()

mode_top_frame.pack(side=LEFT)
volt_top_frame.pack(side=LEFT)
cur_top_frame.pack(side=LEFT)
pow_top_frame.pack(side=LEFT)

label_mon_space1 = Label(master=top_frame, text="", width = 2)
label_mon_space1.pack(side=LEFT)
input_change_button = Button(master=top_frame,text="Enable\nInput",width=7,height=2,bg='LightGrey',font =('Courier New', 16))
input_change_button.pack(side=LEFT)
input_change_button.bind("<Button-1>", input_change_click)

status_labels_frame = Frame(master=top_frame_sur,width=900)
status_label_1 = Label(master=status_labels_frame,text="Wait for\nTrigger")
status_label_2 = Label(master=status_labels_frame,text="Remote\nControl")
status_label_3 = Label(master=status_labels_frame,text="Input\nEnabled")
status_label_4 = Label(master=status_labels_frame,text="Remote\nSense")
status_label_5 = Label(master=status_labels_frame,text="Load Timer\nActive")
status_label_6 = Label(master=status_labels_frame,text="Reversed\nVoltage")
status_label_7 = Label(master=status_labels_frame,text="Over\nVoltage")
status_label_8 = Label(master=status_labels_frame,text="Over\nCurrent")
status_label_9 = Label(master=status_labels_frame,text="Over\nPower")
status_label_10 = Label(master=status_labels_frame,text="Over\nTemp")
status_space_label_1 = Label(master=status_labels_frame,text="")
status_label_1.pack(padx=14,pady=10,side=LEFT)
status_label_2.pack(padx=20,pady=10,side=LEFT)
status_label_3.pack(padx=15,pady=10,side=LEFT)
status_label_4.pack(padx=20,pady=10,side=LEFT)
status_label_5.pack(padx=2,pady=10,side=LEFT)
status_label_6.pack(padx=15,pady=10,side=LEFT)
status_label_7.pack(padx=12,pady=10,side=LEFT)
status_label_8.pack(padx=23,pady=10,side=LEFT)
status_label_9.pack(padx=15,pady=10,side=LEFT)
status_space_label_1.pack(padx=12,pady=10,side=LEFT)
status_label_10.pack(padx=2,pady=10,side=LEFT)
status_labels_frame.pack(side=BOTTOM,fill=X)

status_frame = Frame(master=top_frame_sur)
status_canvas = Canvas(status_frame, width=900, height=50)
status_canvas.pack(side=LEFT,fill=X)
status_light1 = status_canvas.create_rectangle(35,20,55,40, fill = "gray")
status_light2 = status_canvas.create_rectangle(125,20,145,40, fill = "gray")
status_light3 = status_canvas.create_rectangle(215,20,235,40, fill = "gray")
status_light4 = status_canvas.create_rectangle(305,20,325,40, fill = "gray")
status_light5 = status_canvas.create_rectangle(395,20,415,40, fill = "gray")
status_light6 = status_canvas.create_rectangle(485,20,505,40, fill = "gray")
status_light7 = status_canvas.create_rectangle(575,20,595,40, fill = "gray")
status_light8 = status_canvas.create_rectangle(665,20,685,40, fill = "gray")
status_light9 = status_canvas.create_rectangle(755,20,775,40, fill = "gray")
status_light10 = status_canvas.create_rectangle(845,20,865,40, fill = "gray")
status_frame.pack(side=BOTTOM,fill=X)

top_frame.pack(pady=5, fill=X)
top_frame_sur.pack(pady=8,fill=X)
frame_top.pack(fill=X)

# Bot Frame content:

tabControl = ttk.Notebook(master=frame_bot)
tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)
tab3 = ttk.Frame(tabControl)
tabControl.add(tab1, text ='Config')
tabControl.add(tab2, text ='Control')
tabControl.add(tab3, text ='About')

# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- #
#                               Tab 1 content:                                  #
# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- #
# COM Frame
com_frame_sur = ttk.LabelFrame(tab1, text = "COM Settings")
com_frame = Frame(master=com_frame_sur)

var_opt_baud = StringVar()
var_opt_baud.set(opt_ser_baud[2])
var_opt_parity = StringVar()
var_opt_parity.set(opt_ser_parity[0])
var_opt_ports = StringVar()

label_win_ser_ports = Label(master=com_frame, text="Port:")
win_ser_ports = OptionMenu(com_frame, var_opt_ports, *opt_ser_ports, command=com_port_change)
win_ser_ports.config(width=10)
label_win_ser_baud = Label(master=com_frame, text="Baud Rate:")
win_ser_baud = OptionMenu(com_frame, var_opt_baud, *opt_ser_baud, command=com_baud_change)
win_ser_baud.config(width=10)
label_win_ser_parity = Label(master=com_frame, text="Parity:")
win_ser_parity = OptionMenu(com_frame, var_opt_parity, *opt_ser_parity, command=com_parity_change)
win_ser_parity.config(width=10)
label_win_ser_addr = Label(master=com_frame, text="Instrument Address:")
win_ser_addr = Entry(com_frame,justify=CENTER)
win_ser_addr.insert(0,0)
win_ser_addr.config(width=10)
com_connect_button = Button(master=com_frame,text="Connect",width=12)

label_win_ser_ports.pack(side=LEFT)
win_ser_ports.pack(padx=2,pady=2,side=LEFT)
label_win_ser_baud.pack(side=LEFT)
win_ser_baud.pack(padx=2,pady=2,side=LEFT)
label_win_ser_parity.pack(side=LEFT)
win_ser_parity.pack(padx=2,pady=2,side=LEFT)
label_win_ser_addr.pack(side=LEFT)
win_ser_addr.pack(padx=2,pady=2,side=LEFT)
com_frame.pack(padx=2,pady=5,fill=X)
com_connect_button.pack(padx=8,pady=2,side=LEFT)
com_connect_button.bind("<Button-1>", com_button_click)
com_frame.pack(pady=2, fill=X)
com_frame_sur.pack(pady=8,fill=X)

# INSTRUMENT info Frame
inst_frame_sur = ttk.LabelFrame(tab1, text = "Instrument Information")
inst_frame = Frame(master=inst_frame_sur)
label_inst_model = Label(master=inst_frame, text="Model:", width=15)
label_inst_ver = Label(master=inst_frame, text="Version:", width=15)
label_inst_sn = Label(master=inst_frame, text="Serial Number:", width=28)
label_inst_max_rat = Label(master=inst_frame, text="Absolute Maximum Ratings:", width=36)
label_inst_model.pack(padx=2,pady=2,side=LEFT)
label_inst_ver.pack(padx=2,pady=2,side=LEFT)
label_inst_sn.pack(padx=2,pady=2,side=LEFT)
label_inst_max_rat.pack(padx=2,pady=2,side=LEFT)
inst_frame.pack(pady=5, fill=X)
inst_frame_sur.pack(pady=8,fill=X)

# INSTRUMENT config Frame
inst_conframe_sur = ttk.LabelFrame(tab1, text = "Instrument Configuration")
inst_conframe1 = Frame(master=inst_conframe_sur)
inst_conframe2 = Frame(master=inst_conframe_sur)

label_remote_sense = Label(master=inst_conframe1, text="Remote Sense:")
remote_sense_var = IntVar()
remote_sense_R1 = Radiobutton(inst_conframe1, text="Off", variable=remote_sense_var, value=False, command=remote_sense_click)
remote_sense_R2 = Radiobutton(inst_conframe1, text="On", variable=remote_sense_var, value=True, command=remote_sense_click)
label_space_1 = Label(master=inst_conframe1, text="", width=3)
label_local_ctrl = Label(master=inst_conframe1, text="Panel Control Override:")
local_ctrl_var = IntVar()
local_ctrl_var.set(True)
local_ctrl_R1 = Radiobutton(inst_conframe1, text="Off", variable=local_ctrl_var, value=False, command=local_ctrl_click)
local_ctrl_R2 = Radiobutton(inst_conframe1, text="On", variable=local_ctrl_var, value=True, command=local_ctrl_click)
label_space_2 = Label(master=inst_conframe1, text="", width=3)
label_trig_src = Label(master=inst_conframe1, text="Trigger Source:")
trig_src_var = IntVar()
trig_src_R1 = Radiobutton(inst_conframe1, text="Immediate", variable=trig_src_var, value=1, command=trig_src_click)
trig_src_R2 = Radiobutton(inst_conframe1, text="External", variable=trig_src_var, value=2, command=trig_src_click)
trig_src_R3 = Radiobutton(inst_conframe1, text="Bus", variable=trig_src_var, value=3, command=trig_src_click)
label_remote_sense.pack(padx=2,pady=2,side=LEFT)
remote_sense_R1.pack(side=LEFT)
remote_sense_R2.pack(side=LEFT)
label_space_1.pack(side=LEFT)
label_local_ctrl.pack(padx=2,pady=2,side=LEFT)
local_ctrl_R1.pack(side=LEFT)
local_ctrl_R2.pack(side=LEFT)
label_space_2.pack(side=LEFT)
label_trig_src.pack(side=LEFT)
trig_src_R1.pack(side=LEFT)
trig_src_R2.pack(side=LEFT)
trig_src_R3.pack(side=LEFT)

label_maxv = Label(master=inst_conframe2, text="Voltage Limit [V]:")
entry_maxv = Entry(inst_conframe2,justify=CENTER)
entry_maxv.config(width=12)
label_space_3 = Label(master=inst_conframe2, text="", width=4)
label_maxi = Label(master=inst_conframe2, text="Current Limit [A]:")
entry_maxi = Entry(inst_conframe2,justify=CENTER)
entry_maxi.config(width=12)
label_space_4 = Label(master=inst_conframe2, text="", width=4)
label_maxw = Label(master=inst_conframe2, text="Power Limit [W]:")
entry_maxw = Entry(inst_conframe2,justify=CENTER)
entry_maxw.config(width=12)
label_space_5 = Label(master=inst_conframe2, text="", width=3)
max_set_button = Button(master=inst_conframe2,text="Set Limits",width=12)

label_maxv.pack(side=LEFT)
entry_maxv.pack(side=LEFT)
label_space_3.pack(side=LEFT)
label_maxi.pack(side=LEFT)
entry_maxi.pack(side=LEFT)
label_space_4.pack(side=LEFT)
label_maxw.pack(side=LEFT)
entry_maxw.pack(side=LEFT)
label_space_5.pack(side=LEFT)
max_set_button.pack(side=LEFT)
max_set_button.bind("<Button-1>", max_set_button_click)
inst_conframe1.pack(pady=5, fill=X)
inst_conframe2.pack(pady=5, fill=X)
inst_conframe_sur.pack(pady=8,fill=X)

# Setting save/load Frame
setting_frame_sur = ttk.LabelFrame(tab1, text = "Instrument Config Store/Recall")
setting_frame = Frame(master=setting_frame_sur)
label_setting_slot = Label(master=setting_frame, text="    Slot Number:")
var_opt_setting_slot = IntVar()
setting_slot_opt = OptionMenu(setting_frame, var_opt_setting_slot, *op_setting_slot)
setting_slot_opt.config(width=6)
label_setting_space = Label(master=setting_frame, text="", width=41)
setting_store_button = Button(master=setting_frame,text="Store",width=10)
setting_recall_button = Button(master=setting_frame,text="Recall",width=10)
var_opt_setting_slot.set(1)
label_setting_slot.pack(padx=5, side=LEFT)
setting_slot_opt.pack(padx=5, pady=2, side=LEFT)
label_setting_space.pack(side=LEFT)
setting_store_button.pack(padx=30, side=LEFT)
setting_store_button.bind("<Button-1>", store_settings_click)
setting_recall_button.pack(padx=10, side=LEFT)
setting_recall_button.bind("<Button-1>", recall_settings_click)
setting_frame.pack(pady=5, fill=X)
setting_frame_sur.pack(pady=8,fill=X)

# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- #
#                               Tab 2 content:                                  #
# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- #
# Mode Frame
mode_frame_sur = ttk.LabelFrame(tab2, text = "Mode Selection")
mode_frame_sur.grid(padx=20, pady=20)
mode_frame = Frame(master=mode_frame_sur)
fixed_frame_sur = ttk.LabelFrame(mode_frame, text = "Mode")
fixed_frame = Frame(master=fixed_frame_sur)
spec_mode_frame_sur = ttk.LabelFrame(mode_frame, text = "Function")
spec_mode_frame = Frame(master=spec_mode_frame_sur)
mode_var = IntVar()
mode_R1 = Radiobutton(fixed_frame, text="Const Current (CC)", variable=mode_var, value=1, command=mode_click)
mode_R2 = Radiobutton(fixed_frame, text="Const Voltage (CV)", variable=mode_var, value=2, command=mode_click)
mode_R3 = Radiobutton(fixed_frame, text="Const Power (CW)", variable=mode_var, value=3, command=mode_click)
mode_R4 = Radiobutton(fixed_frame, text="Const Resistance (CR)", variable=mode_var, value=4, command=mode_click)
spec_mode_var = IntVar()
spec_mode_R1 = Radiobutton(spec_mode_frame, text="Fixed", variable=spec_mode_var, value=1, command=spec_mode_click)
spec_mode_R2 = Radiobutton(spec_mode_frame, text="Transient", variable=spec_mode_var, value=2, command=spec_mode_click)
spec_mode_R3 = Radiobutton(spec_mode_frame, text="Short", variable=spec_mode_var, value=3, command=spec_mode_click)
label_space_6 = Label(master=fixed_frame, text="", width=0)
label_space_7 = Label(master=fixed_frame, text="", width=0)
label_space_8 = Label(master=fixed_frame, text="", width=0)
label_space_9 = Label(master=mode_frame, text="", width=2)
label_space_10 = Label(master=mode_frame, text="", width=0)
mode_R1.pack(side=LEFT)
mode_R2.pack(side=LEFT)
mode_R3.pack(side=LEFT)
mode_R4.pack(side=LEFT)
fixed_frame.pack()
fixed_frame_sur.pack(side=LEFT)
spec_mode_R1.pack(side=LEFT)
spec_mode_R2.pack(side=LEFT)
spec_mode_R3.pack(side=LEFT)
label_space_9.pack(side=LEFT)
spec_mode_frame.pack()
spec_mode_frame_sur.pack(side=LEFT)

mode_frame.pack(pady=5, fill=X)
mode_frame_sur.pack(pady=8,fill=X)

# Set CVWR Values Frame
val_frame_sur = ttk.LabelFrame(tab2, text = "Set C/V/W/R")
val_frame = Frame(master=val_frame_sur)
label_seti = Label(master=val_frame, text="Current [A]:")
entry_seti = Entry(val_frame,justify=CENTER)
entry_seti.config(width=10)
label_setv = Label(master=val_frame, text="Voltage [V]:")
entry_setv = Entry(val_frame,justify=CENTER)
entry_setv.config(width=10)
label_setw = Label(master=val_frame, text="Power [W]:")
entry_setw = Entry(val_frame,justify=CENTER)
entry_setw.config(width=10)
label_setr = Label(master=val_frame, text="Resistance [Ohm]:")
entry_setr = Entry(val_frame,justify=CENTER)
entry_setr.config(width=10)
val_set_button = Button(master=val_frame,text="Set Values",width=12)
label_space_11 = Label(master=val_frame, text="", width=1)
label_space_12 = Label(master=val_frame, text="", width=1)
label_space_13 = Label(master=val_frame, text="", width=1)
label_space_14 = Label(master=val_frame, text="", width=4)

label_seti.pack(side=LEFT)
entry_seti.pack(side=LEFT)
label_space_11.pack(side=LEFT)
label_setv.pack(side=LEFT)
entry_setv.pack(side=LEFT)
label_space_12.pack(side=LEFT)
label_setw.pack(side=LEFT)
entry_setw.pack(side=LEFT)
label_space_13.pack(side=LEFT)
label_setr.pack(side=LEFT)
entry_setr.pack(side=LEFT)
label_space_14.pack(side=LEFT)
val_set_button.pack(side=LEFT)
val_set_button.bind("<Button-1>", val_set_button_click)
val_frame.pack(pady=5, fill=X)
val_frame_sur.pack(pady=8,fill=X)

# Capacity Frame
cap_frame_sur = ttk.LabelFrame(tab2, text = "Capacity Meter")
cap_frame = Frame(master=cap_frame_sur)
label_cap_ah = Label(master=cap_frame, text="Charge [AH]:")
label_val_ah = Label(master=cap_frame, text=str(round(cap_ah,3)), width=9)
label_cap_wh = Label(master=cap_frame, text="Energy [WH]:")
label_val_wh = Label(master=cap_frame, text=str(round(cap_wh,3)),width=9)
cap_reset_button = Button(master=cap_frame,text="Reset",width=6)
label_cap_vmin = Label(master=cap_frame, text="Vmin:")
check_cap_vmin_var = IntVar()
check_cap_vmin = Checkbutton(cap_frame, text="Enable", var=check_cap_vmin_var)
entry_cap_vmin = Entry(cap_frame,justify=CENTER)
entry_cap_vmin.config(width=8)
cap_vmin_set_button = Button(master=cap_frame,text="Set",width=6)
label_cap_vmin2 = Label(master=cap_frame, text=" Voltage [V]:")
entry_cap_vmin.delete(0, END)
entry_cap_vmin.insert(0, str(round(vmin,3)))
label_space_15 = Label(master=cap_frame, text="", width=1)
label_space_16 = Label(master=cap_frame, text="", width=1)
label_space_17 = Label(master=cap_frame, text="", width=6)
label_space_18 = Label(master=cap_frame, text="", width=1)

label_cap_ah.pack(side=LEFT)
label_val_ah.pack(side=LEFT)
label_space_15.pack(side=LEFT)
label_cap_wh.pack(side=LEFT)
label_val_wh.pack(side=LEFT)
label_space_16.pack(side=LEFT)
cap_reset_button.pack(side=LEFT)
cap_reset_button.bind("<Button-1>", cap_reset_button_click)
label_space_17.pack(side=LEFT)
label_cap_vmin.pack(side=LEFT)
check_cap_vmin.pack(side=LEFT)
label_cap_vmin2.pack(side=LEFT)
entry_cap_vmin.pack(side=LEFT)
label_space_18.pack(side=LEFT)
cap_vmin_set_button.pack(side=LEFT)
cap_vmin_set_button.bind("<Button-1>", cap_vmin_set_click)
cap_frame.pack(pady=5, fill=X)
cap_frame_sur.pack(pady=8,fill=X)

# Transient Frame
tran_frame_sur = ttk.LabelFrame(tab2, text = "Transient Parameters")
tran_frame = Frame(master=tran_frame_sur)
label_tran_val1 = Label(master=tran_frame, text="I1 [A]:", width=9)
entry_tran_val1 = Entry(tran_frame,justify=CENTER)
entry_tran_val1.config(width=8)
label_tran_time1 = Label(master=tran_frame, text="T1 [s]:")
entry_tran_time1 = Entry(tran_frame,justify=CENTER)
entry_tran_time1.config(width=8)
label_tran_val2 = Label(master=tran_frame, text="I2 [A]:", width=9)
entry_tran_val2 = Entry(tran_frame,justify=CENTER)
entry_tran_val2.config(width=8)
label_tran_time2 = Label(master=tran_frame, text="T2 [s]:")
entry_tran_time2 = Entry(tran_frame,justify=CENTER)
entry_tran_time2.config(width=8)
label_tran_mode = Label(master=tran_frame, text="    Mode:")
var_tran_op = StringVar()
tran_op_opt = OptionMenu(tran_frame, var_tran_op, *opt_tran_op)
var_tran_op.set(opt_tran_op[0])
tran_op_opt.config(width=10)
tran_set_button = Button(master=tran_frame,text="Set",width=6)
tran_trig_button = Button(master=tran_frame,text="Trigger",width=6)

label_tran_val1.pack(side=LEFT)
entry_tran_val1.pack(side=LEFT)
label_tran_time1.pack(side=LEFT)
entry_tran_time1.pack(side=LEFT)
label_tran_val2.pack(side=LEFT)
entry_tran_val2.pack(side=LEFT)
label_tran_time2.pack(side=LEFT)
entry_tran_time2.pack(side=LEFT)
label_tran_mode.pack(side=LEFT)
tran_op_opt.pack(side=LEFT,padx=3)
tran_set_button.pack(side=LEFT,padx=15)
tran_set_button.bind("<Button-1>", tran_set_click)
tran_trig_button.pack(side=LEFT,padx=15)
tran_trig_button.bind("<Button-1>", tran_trig_click)
tran_frame.pack(pady=5, fill=X)
tran_frame_sur.pack(pady=8,fill=X)

# Timer Frame
timer_frame_sur = ttk.LabelFrame(tab2, text = "Load Timer")
timer_frame = Frame(master=timer_frame_sur)
label_timer1 = Label(master=timer_frame, text="Load max ON time [s]:")
entry_timer = Entry(timer_frame,justify=CENTER)
entry_timer.config(width=10)
timer_set_button = Button(master=timer_frame,text="Set",width=6)
label_timer2 = Label(master=timer_frame, text=" ")
label_timer3 = Label(master=timer_frame, text="Timer Mode:")
timer_enable_var = IntVar()
timer_enable_R1 = Radiobutton(timer_frame, text="Disabled", variable=timer_enable_var, value=False, command=timer_enable_click)
timer_enable_R2 = Radiobutton(timer_frame, text="Enabled", variable=timer_enable_var, value=True, command=timer_enable_click)
label_timer1.pack(side=LEFT,padx=10)
entry_timer.pack(side=LEFT)
timer_set_button.pack(side=LEFT,padx=20)
timer_set_button.bind("<Button-1>", timer_set_click)
label_timer2.pack(side=LEFT,padx=100)
label_timer3.pack(side=LEFT,padx=20)
timer_enable_R1.pack(side=LEFT)
timer_enable_R2.pack(side=LEFT)
timer_frame.pack(pady=5, fill=X)
timer_frame_sur.pack(pady=8,fill=X)

# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- #
#                               Tab 3 content:                                  #
# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- #
# About Frame
about_frame = Frame(master=tab3)
about_label = Label(master=about_frame, text="BK8500 Controller app v1.0\nFor use with BK Precision 8500 series DC electronic loads\nwww.TolisDIY.com",justify=LEFT)
about_label.pack(side=LEFT)
about_frame.pack(fill=BOTH)

tabControl.pack(expand = True, fill="both")
frame_bot.pack(fill=X)

# Log Frame
log_frame_sur = ttk.LabelFrame(window, text = "Command Log")
log_frame = Frame(master=log_frame_sur)
log_text_box = ScrolledText(master=log_frame,width=800,height=500)
log_text_box.pack(side=LEFT, fill=Y)
log_frame.pack(pady=5, fill=X)
log_frame_sur.pack(pady=8,fill=X)

print = super_print(log_text_box)(print)
t = RepeatableTimer(update_prd, timed_status_update)

window.mainloop()