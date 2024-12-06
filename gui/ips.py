'''iPS control frame'''

# Imports
import tkinter as tk    # Gui package
from tkinter import ttk # Fancier widgets
from tkinter import messagebox

from gui.funct import Strip_T, List_sensors

# Logging
import datetime # A format for dates and time
import csv # For importing and exporting CSV files
import os # For compiling directory paths

import logging
logger = logging.getLogger('log')     # Set the logger

# Global variables
LOG_TIME = 20*60*1000 # 20 min
SWITCH_TOLERANCE = 0.001 # Heater switch tolerance
MAIN_PSU = 'GRPZ' # Main board for driving magnet
MAIN_LVL = 'DB5.L1' # Main board for cryo level sensors
MAIN_TEMP = 'MB1.T1' # Main board for temperature sensor



class IPS_frame(tk.Frame):
    '''The controll frame for IPS'''
    def __init__(self, parent, ports):
        tk.Frame.__init__(self, parent, width=300, height=900, padx=5, pady=5)
        self.parent = parent
        self.ports = ports
        self.Widgets()

        # Fill in parameters from iPS
        self.Load_parameters()


    def Widgets(self):
        '''Shapes the frame's widgets'''
        # Label
        self.label_title = ttk.Label(self, text='Mercury iPS')
        self.label_title.config(font=('Courier', 16))
        self.label_title.pack(side='top', fill='x', padx=10)

        
        # Status framerts
        self.frame_status = Status(self, self.ports)
        self.frame_status.pack(side='top', fill='x', padx=5, pady=5)

        # Set frame
        self.frame_set = SetF(self, self.ports)
        self.frame_set.pack(side='top', fill='x', padx=5, pady=5)

        # Switch frame
        self.frame_switch = Switch(self, self.ports)
        self.frame_switch.pack(side='top', fill='x', padx=5, pady=5)

        # Ramp frame
        self.frame_ramp = Ramp(self, self.ports)
        self.frame_ramp.pack(side='top', fill='x', padx=5, pady=5)

        # Sensor frame
        self.frame_sensors = Sensors(self, self.ports)
        self.frame_sensors.pack(side='top', fill='x', padx=5, pady=5)

        # Select frame
        self.frame_select = Select(self, self.ports)
        self.frame_select.pack(side='top', fill='x', padx=5 , pady=5)

        # Load parameters
        self.button_load = ttk.Button(self, text='Load from iPS',
            command=self.Load_parameters, width=20)
        self.button_load.pack(side='top',pady=10)


    def Load_parameters(self):
        '''Talks to IPS and refreshes all values in entry boxes'''
        logger.info('Loading IPS parameters from:'+
            self.frame_select.var_sens.get())

        flog = self.ports.Get_Fstatus(self.frame_select.var_sens.get())
        fset = self.ports.Get_Fset(self.frame_select.var_sens.get())
        fmode = self.ports.Get_Fmode(self.frame_select.var_sens.get())
        fsensors = self.ports.Get_Fsensors(self.frame_select.var_sens.get(),
            self.frame_select.var_lvl.get(),self.frame_select.var_temp.get())

        self.frame_status.Update(flog)
        self.frame_set.Update(fset)
        self.frame_switch.Update(fmode[0])
        self.frame_ramp.Update(fmode[1])
        self.frame_sensors.Update(fsensors)

    
    def Monitor_ramp(self):
        '''Talks to iPS and refreshes values in ramp and status'''
        flog = self.ports.Get_Fstatus(self.frame_select.var_sens.get())
        fmode = self.ports.Get_Fmode(self.frame_select.var_sens.get())

        self.frame_status.Update(flog)
        self.frame_switch.Update(fmode[0])
        self.frame_ramp.Update(fmode[1])



class Status(tk.LabelFrame):
    '''Status frame and inner objects'''
    def __init__(self, parent, ports):
        '''Calls init method of LabelFrame and fills up frame'''
        tk.LabelFrame.__init__(self, parent, text='Status', padx=10, pady=5)
        self.parent = parent
        self.ports = ports
        self.Widgets()


    def Widgets(self):
        '''Shapes the frame's widgets'''
        # Labels
        ttk.Label(self, text='Field').grid(row=0, column=0)
        ttk.Label(self, text='Field target').grid(row=0, column=2)

        ttk.Label(self, text='Voltage').grid(row=2, column=0)
        ttk.Label(self, text='Current').grid(row=2, column=2)

        ttk.Label(self, text='Actual field rate').grid(row=4, column=0)
        ttk.Label(self, text='Persistent field').grid(row=4, column=2)

        # Spacer
        ttk.Label(self, text='  ').grid(row=0,column=1)
        self.grid_columnconfigure(1, weight=1) # Alows stretch and centering

        # Entries
        self.var_field = tk.StringVar(self)
        self.entry_field = ttk.Entry(self, textvariable=self.var_field,
            justify='center', width=14, state='readonly')
        self.entry_field.grid(row=1, column=0)

        self.var_fset = tk.StringVar(self)
        self.entry_fset = ttk.Entry(self, textvariable=self.var_fset,
            justify='center', width=14, state='readonly')
        self.entry_fset.grid(row=1, column=2)

        self.var_voltage = tk.StringVar(self)
        self.entry_voltage = ttk.Entry(self, textvariable=self.var_voltage,
            justify='center', width=14, state='readonly')
        self.entry_voltage.grid(row=3, column=0)

        self.var_current = tk.StringVar(self)
        self.entry_current = ttk.Entry(self, textvariable=self.var_current,
            justify='center', width=14, state='readonly')
        self.entry_current.grid(row=3, column=2)

        self.var_frate = tk.StringVar(self)
        self.entry_frate = ttk.Entry(self, textvariable=self.var_frate,
            justify='center', width=14, state='readonly')
        self.entry_frate.grid(row=5, column=0)

        self.var_pfield = tk.StringVar(self)
        self.entry_pfield = ttk.Entry(self, textvariable=self.var_pfield,
            justify='center', width=14, state='readonly')
        self.entry_pfield.grid(row=5, column=2)

    
    def Update(self, flog):
        '''Updates values in entries from iPS'''
        logger.info('Updating IPS status: '+ str(flog))
        self.var_field.set(flog[1])
        self.var_fset.set(flog[2])
        self.var_voltage.set(flog[3])
        self.var_current.set(flog[4])
        self.var_frate.set(flog[5])
        self.var_pfield.set(flog[6])



class SetF(tk.LabelFrame):
    '''Set field frame and inner objects'''
    def __init__(self, parent, ports):
        '''Calls init method of LabelFrame and fills up frame'''
        tk.LabelFrame.__init__(self, parent, text='Set Field', padx=10,
            pady=5)
        self.parent = parent
        self.ports = ports
        self.Widgets()


    def Widgets(self):
        '''Shapes the frame's widgets'''
        # Labels
        ttk.Label(self, text='Target field:').grid(row=0, column=0, sticky='E')
        ttk.Label(self, text='Ramp rate:').grid(row=1, column=0, sticky='E')
        ttk.Label(self, text='Confirm').grid(row=2, column=0, sticky='E')

        ttk.Label(self, text='T').grid(row=0, column=3, sticky='W')
        ttk.Label(self, text='T/min').grid(row=1, column=3, sticky='W')

        # Spacer
        ttk.Label(self, text='  ').grid(row=0, column=1)
        self.grid_columnconfigure(1, weight=1) # Alows stretch and centering

        # Entries
        self.var_set = tk.StringVar(self)
        self.entry_set = ttk.Entry(self, width=7, textvariable=self.var_set,
            justify='right')
        self.entry_set.grid(row=0, column=2)

        self.var_rate = tk.StringVar(self)
        self.entry_rate = ttk.Entry(self, width=7, textvariable=self.var_rate,
            justify='right')
        self.entry_rate.grid(row=1, column=2)

        # Button
        self.button_set = ttk.Button(self, text='Set field',
            command=self.Set, width=10)
        self.button_set.grid(row=2, column=2, columnspan=2)


    def Set(self):
        '''Confirms written values and sends to iPS'''
        values = [
            self.var_set.get(),
            self.var_rate.get()
        ]
        logger.info(('Setting Field:', values))
        sens = self.parent.frame_select.var_sens.get()
        logger.debug(sens)
        self.ports.Set_Fset(sens, values)



    def Update(self, fset):
        '''Updates previously set values from iPS'''
        logger.info('Updating previously set field values from IPS: '+str(fset))
        self.var_set.set(Strip_T(fset[0]))
        self.var_rate.set(Strip_T(fset[1]))



class Switch(tk.LabelFrame):
    '''Switch heater frame and inner objects'''
    def __init__(self, parent, ports):
        '''Calls init method of LabelFrame and fills up frame'''
        tk.LabelFrame.__init__(self, parent, text='Switch heater mode',
            padx=10, pady=5)
        self.parent = parent
        self.ports = ports
        self.Widgets()


    def Widgets(self):
        '''Shapes the frame's widgets'''
        # Spacer
        self.grid_columnconfigure(0, weight=1) # Alows stretch and centering

        # Radio button switch heater
        self.list_switch = ['ON', 'OFF']
        self.var_switch = tk.IntVar(self)
        self.var_switch.set(-1) # Doesnt show an option on start
        self.radio_switch1 = ttk.Radiobutton(self, text='On', value=0,
            variable=self.var_switch)
        self.radio_switch1.grid(row=1, column=0, sticky='W')
        self.radio_switch2 = ttk.Radiobutton(self, text='Off', value=1,
            variable=self.var_switch)
        self.radio_switch2.grid(row=2, column=0, sticky='W')

        # Button
        self.button_set = ttk.Button(self, text='Set',
            command=self.Set, width=10)
        self.button_set.grid(row=8, column=0)

    
    def Set(self):
        '''Confirms written values and sends to iPS'''
        # Get params
        sens = self.parent.frame_select.var_sens.get()
        value = self.list_switch[self.var_switch.get()]
        # Get PSU and magnet fields for safety check
        field_psu = self.ports.ips.__dict__[sens].Read_option(
            'FLD', warn=False)
        field_pers = self.ports.ips.__dict__[sens].Read_option(
            'PFLD', warn=False)
        field_psu = float(field_psu[:-1])
        field_pers = float(field_pers[:-1])
        if abs(field_psu-field_pers) > SWITCH_TOLERANCE:
            logger.error('Persistent field differs from current field')
            messagebox.showerror('Could not switch heater!',
                'The persistent field and current field are not the same!')
        else :
            # Log
            logger.info('Setting switch heater mode to: '+ value)
            # Send value to iPS
            if not self.ports.ips.__dict__[sens].Set_option('SWHT', value):
                logger.error('Failed to set switch heater to '+value)


    def Update(self, mode):
        '''Updates values from IPS'''
        logger.info('Updating switch heater mode: '+ str(mode))
        if mode == 'ON': self.var_switch.set(0)
        elif mode == 'OFF': self.var_switch.set(1)
        else: logger.warning('Unknown switch reply: '+ mode)
        # Study this guy....



class Ramp(tk.LabelFrame):
    '''Ramp frame and inner objects'''
    def __init__(self, parent, ports):
        '''Calls init method of LabelFrame and fills up frame'''
        tk.LabelFrame.__init__(self, parent, text='Ramp mode', padx=10,
            pady=5)
        self.parent = parent
        self.ports = ports

        # List of possible states
        self.list_ramp = ['HOLD', 'RTOS', 'RTOZ', 'CLMP']
        self.dict_ramp = {
            'HOLD': 'Hold',
            'RTOS': 'To set',
            'RTOZ': 'To zero',
            'CLMP': 'Clamp'
        }
        self.var_ramp = tk.StringVar(self)
        self.Widgets()


    def Widgets(self):
        '''Shapes the frame's widgets'''
        # Spacer
        ttk.Label(self, text='  ').grid(row=1, column=1)
        self.grid_columnconfigure(1, weight=1) # Alows stretch and centering

        # Buttons
        self.button_hold = ttk.Button(self, text='Hold',
            command=lambda:self.Set('HOLD'), width=12)
        self.button_hold.grid(row=1, column=0)

        self.button_clamp = ttk.Button(self, text='Clamp',
            command=lambda:self.Set('CLMP'), width=12)
        self.button_clamp.grid(row=1, column=2)

        self.button_to_set = ttk.Button(self, text='To set',
            command=lambda:self.Set('RTOS'), width=12)
        self.button_to_set.grid(row=2, column=0)

        self.button_to_zero = ttk.Button(self, text='To zero',
            command=lambda:self.Set('RTOZ'), width=12)
        self.button_to_zero.grid(row=2, column=2)

        # Show last state
        ttk.Label(self, text='Last state:').grid(row=0, column=0, sticky='E')
        self.entry_ramp = ttk.Entry(self, textvariable=self.var_ramp,
            justify='center', width=10, state='readonly')
        self.entry_ramp.grid(row=0, column=2)


    def Set(self, mode):
        '''Sends the button command to iPS'''
        # Get sensor
        sens = self.parent.frame_select.var_sens.get()
        # Log
        logger.info('Setting ramp mode: '+mode)
        self.var_ramp.set(self.dict_ramp[mode])
        # Send command
        if not self.ports.ips.__dict__[sens].Set_option('ACTN', mode):
            logger.error('Failed to set switch heater to '+mode)
        self.Monitor()


    def Monitor(self):
        '''Keeps refreshing the ramp window untill Hold is reached'''
        self.parent.Monitor_ramp()

        # Repeat untill Hold is reached
        if self.var_ramp.get() not in ['Hold', 'Clamp']:
            self.repeat = self.after(10*1000, self.Monitor)
        else: self.repeat = None # Remove reference to repeat event

    
    def Update(self, mode):
        '''Updates values from iPS'''
        logger.info('Updating ramp mode: '+ str(mode))
        self.var_ramp.set(self.dict_ramp[mode])



class Sensors(tk.LabelFrame):
    '''Sensor frame and inner objects'''
    def __init__(self, parent, ports):
        '''Calls init method of LabelFrame and fills up frame'''
        tk.LabelFrame.__init__(self, parent, text='Sensors', padx=10, pady=5)
        self.parent = parent
        self.ports = ports
        self.Widgets()

        self.file_end = '_Sensor.log'
        # Create directory if non existent
        self.file_directory = os.path.join('log_files','sensors')
        try: os.mkdir('log_files')
        except: pass
        try: os.mkdir(self.file_directory)
        except: pass

        # Start logging on self
        self.logging = self.after(10, self.Log)


    def Widgets(self):
        '''Shapes the frame's widgets'''
        # Labels
        ttk.Label(self, text='Helium level').grid(row=0, column=0)
        ttk.Label(self, text='Nitrogen level').grid(row=0, column=2)
        #ttk.Label(self, text='Magnet temperature').grid(row=3, column=0,
        #    columnspan=3)

        # Spacer
        ttk.Label(self, text='  ').grid(row=0, column=1)
        self.grid_columnconfigure(1, weight=1) # Alows stretch and centering

        # Entries
        self.var_resistance = tk.StringVar(self)
        self.entry_resistance = ttk.Entry(self, width=12, state='readonly',
            textvariable=self.var_resistance, justify='center')
        self.entry_resistance.grid(row=1, column=0)

        self.var_freq = tk.StringVar(self)
        self.entry_freq = ttk.Entry(self, width=12, state='readonly',
            textvariable=self.var_freq, justify='center')
        self.entry_freq.grid(row=1, column=2)

        # Temperature sensor not used yet
        """
        self.var_temp = tk.StringVar(self)
        self.entry_temp = ttk.Entry(self, width=12, state='readonly',
            textvariable=self.var_temp, justify='center')
        self.entry_temp.grid(row=4, column=0, columnspan=3)
        """

        # Status bars
        self.var_helium = tk.DoubleVar(self)
        self.bar_helium = ttk.Progressbar(self, variable=self.var_helium,
            length=68)
        self.bar_helium.grid(row=2, column=0)

        self.var_nitrogen = tk.DoubleVar(self)
        self.bar_nitrogen = ttk.Progressbar(self, variable=self.var_nitrogen,
            length=68)
        self.bar_nitrogen.grid(row=2, column=2)


    def Log(self):
        '''Function for continous logging of sensor data into file'''
        # Fetch fresh values
        log = self.ports.Get_Fsens(self.parent.frame_select.var_lvl.get())
        # Update self
        self.Update(log[1:])

        # Define file parameters
        file_name = log[0].strftime('%Y%m%d') + self.file_end
        file_path = os.path.join(self.file_directory, file_name)

        with open(file_path, 'a', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            # Add line
            line = []
            line.append(log[0].strftime('%H:%M:%S'))
            for i in log[1:]:
                try:
                    line.append(float(i[:-1])) # Strip the % unit
                except TypeError:
                    line.append('') # Write empty string, if None
            writer.writerow(line)

        # Continue logging
        self.logging = self.after(LOG_TIME, self.Log)


    def Update(self, fsensors):
        '''Updates values from iPS'''
        logger.info('Updating IPS sensor status: '+str(fsensors))
        try:
            self.var_helium.set(float(fsensors[0][:-1]))
            self.var_nitrogen.set(float(fsensors[1][:-1]))
        except: pass
        # Use percentage values instead
        self.var_resistance.set(fsensors[0])
        self.var_freq.set(fsensors[1])
        
        try:
            self.parent.parent.menu.cryo_app.Update(datetime.datetime.now(), float(fsensors[0][:-1]), float(fsensors[1][:-1]))
        except Exception as e:
            pass # usual error is that the cryo log does not exist. 
            # print("Updating cryo log failed with error", e) # for debuging
        #Cryo_application.Update(Cryo_application, datetime.datetime.timestamp(datetime.datetime.now()), float(fsensors[0][:-1]), float(fsensors[1][:-1]))

        #self.var_resistance.set(fsensors[2])
        #self.var_freq.set(fsensors[3])
        # Temperature sensor not used yet
        #self.var_temp.set(fsensors[4])



class Select(tk.Frame):
    '''Sensor frame and inner objects'''
    def __init__(self, parent, ports):
        '''Calls init method of LabelFrame and fills up frame'''
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.ports = ports
        self.Widgets()


    def Widgets(self):
        '''Shapes the frame's widgets'''
        # Labels
        ttk.Label(self, text='PSU board select').grid(row=0, column=0,
            sticky='E')
        ttk.Label(self, text='Level board').grid(row=1, column=0,
            sticky='E')
        ttk.Label(self, text='Temperature board').grid(row=2, column=0,
            sticky='E')

        # Spacer
        ttk.Label(self, text='  ').grid(row=0, column=1)
        self.grid_columnconfigure(1, weight=1) # Alows stretch and centering

        # PSU board/sens
        self.list_sens = List_sensors('PSU', self.ports.ips)
        self.var_sens = tk.StringVar(self)
        self.var_sens.set(MAIN_PSU) # Default board
        self.combo_sens = ttk.Combobox(self, width=7, state='disabled',
            values=self.list_sens, textvar=self.var_sens)
        self.combo_sens.grid(row=0, column=2)
        # Disabled to prevent tinkering, can change to 'readonly'

        # Select lvl board
        self.list_lvl = List_sensors('LVL', self.ports.ips)
        self.var_lvl = tk.StringVar(self)
        self.var_lvl.set(MAIN_LVL) # Default board
        self.combo_lvl = ttk.Combobox(self, width=7, state='disabled',
            values=self.list_lvl, textvar=self.var_lvl)
        self.combo_lvl.grid(row=1, column=2)
        # Disabled to prevent tinkering, can change to 'readonly'

        # Select temperature board
        self.list_temp = List_sensors('TEMP', self.ports.ips)
        self.var_temp = tk.StringVar(self)
        self.var_temp.set(MAIN_TEMP) # Default board
        self.combo_temp = ttk.Combobox(self, width=7, state='disabled',
            values=self.list_temp, textvar=self.var_temp)
        self.combo_temp.grid(row=2, column=2)
        # Disabled to prevent tinkering, can change to 'readonly'


