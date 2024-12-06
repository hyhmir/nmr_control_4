'''Itc controlling frame'''

# Imports
import tkinter as tk    # Gui package
from tkinter import ttk # Fancier widgets
from tkinter import messagebox

from gui.funct import Strip_T, List_sensors

import logging
logger = logging.getLogger('log')     # Set the logger

# Global variables
MAIN_SENSOR = 'MB1.T1' # Sensor used for temperature loop



class ITC_frame(tk.Frame):
    '''The controll frame for ITC'''
    def __init__(self, parent, ports):
        tk.Frame.__init__(self, parent, width=300, height=900, padx=5, pady=5)
        self.parent = parent
        self.ports = ports
        self.Widgets()

        # Fill in parameters from iTC
        self.Load_parameters()


    def Widgets(self):
        '''Shapes the frame's widgets'''
        # Label
        self.label_title = ttk.Label(self, text='Mercury iTC')
        self.label_title.config(font=('Courier', 16))
        self.label_title.pack(side='top', fill='x', padx=10)

        # Status frame
        self.frame_status = Status(self, self.ports)
        self.frame_status.pack(side='top', fill='x', padx=5, pady=5)

        # Set frame
        self.frame_set = SetT(self, self.ports)
        self.frame_set.pack(side='top', fill='x', padx=5, pady=5)
    
        # Manual frame
        self.frame_manual = Manual(self, self.ports)
        self.frame_manual.pack(side='top', fill='x', padx=5, pady=5)

        # # Loop frame
        # self.frame_loop = Loop(self, self.ports)
        # self.frame_loop.pack(side='top', fill='x', padx=5, pady=5)

        # # Heater limits frame
        # self.frame_limits = Limits(self, self.ports)
        # self.frame_limits.pack(side='top', fill='x', padx=5, pady=5)

        # Select sensor frame
        self.frame_sensor = Select(self, self.ports)
        self.frame_sensor.pack(side='top', fill='x', padx=5, pady=5)
        self.var_sens = self.frame_sensor.var_sens

        # Load parameters
        self.button_load = ttk.Button(self, text='Load from iTC',
            command=self.Load_parameters, width=20)
        self.button_load.pack(side='top',pady=5)


    def Load_parameters(self):
        '''Talks to ITC and refreshes all values in entry boxes'''
        logger.info('Loading ITC parameters from'+ self.var_sens.get())
        tset = self.ports.Get_Tset(self.var_sens.get())
        tmanual = self.ports.Get_Tmanual(self.var_sens.get())
        tloop = self.ports.Get_Tloop(self.var_sens.get())
        tstatus = self.ports.Get_Tstatus(self.var_sens.get(), tloop[3])
        #tlimits = self.ports.Get_Tlimits(self.var_sens.get(), tloop[3])

        self.frame_status.Update(tstatus)
        self.frame_set.Update(tset)
        self.frame_manual.Update(tmanual)
        #self.frame_loop.Update(tloop)
        #self.frame_limits.Update(tlimits)



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
        ttk.Label(self, text='Temperature').grid(row=0, column=0)
        ttk.Label(self, text='Setpoint').grid(row=0, column=2)

        ttk.Label(self, text='Heater %').grid(row=2, column=0)
        ttk.Label(self, text='Flow %').grid(row=2, column=2)

        ttk.Label(self, text='Heater Power').grid(row=4, column=0)
        ttk.Label(self, text='Needle position').grid(row=4, column=2)

        # Spacer
        ttk.Label(self, text='  ').grid(row=0, column=1)
        self.grid_columnconfigure(1, weight=1) # Alows stretch and centering

        # Entries
        self.var_temp = tk.StringVar(self)
        self.entry_temp = ttk.Entry(self, textvariable=self.var_temp,
            justify='center', width=12, state='readonly')
        self.entry_temp.grid(row=1, column=0)

        self.var_tset = tk.StringVar(self)
        self.entry_tset = ttk.Entry(self, textvariable=self.var_tset,
            justify='center', width=12, state='readonly')
        self.entry_tset.grid(row=1, column=2)

        self.var_power = tk.StringVar(self)
        self.entry_power = ttk.Entry(self, textvariable=self.var_power,
            justify='center', width=12, state='readonly')
        self.entry_power.grid(row=5, column=0)

        self.var_needle = tk.StringVar(self)
        self.entry_needle = ttk.Entry(self, textvariable=self.var_needle,
            justify='center', width=12, state='readonly')
        self.entry_needle.grid(row=5, column=2)

        # Status bars
        self.var_heater = tk.DoubleVar(self)
        self.bar_heater = ttk.Progressbar(self, variable=self.var_heater,
            length=68)
        self.bar_heater.grid(row=3, column=0)

        self.var_flow = tk.DoubleVar(self)
        self.bar_flow = ttk.Progressbar(self, variable=self.var_flow,
            length=68)
        self.bar_flow.grid(row=3, column=2)

    
    def Update(self, tstatus):
        '''Updates values from iTC
            (time, temperature, setpoint, heater, flow, power)'''
        logger.info('Updating iTC status: '+ str(tstatus))
        self.var_temp.set(tstatus[1])
        self.var_tset.set(tstatus[2])
        self.var_heater.set(tstatus[3])
        self.var_flow.set(tstatus[4])
        self.var_power.set(tstatus[5])
        self.var_needle.set(tstatus[4])



class SetT(tk.LabelFrame):
    '''Set temperature frame and inner objects'''
    def __init__(self, parent, ports):
        '''Calls init method of LabelFrame and fills up frame'''
        tk.LabelFrame.__init__(self, parent, text='Set Temperature', padx=10,
            pady=5)
        self.parent = parent
        self.ports = ports
        self.Widgets()


    def Widgets(self):
        '''Shapes the frame's widgets'''
        # Labels
        ttk.Label(self, text='Set T:').grid(row=0, column=0, sticky='E')
        ttk.Label(self, text='Ramp rate:').grid(row=1, column=0, sticky='E')
        ttk.Label(self, text='Enable ramp').grid(row=2, column=0, sticky='E')
        ttk.Label(self, text='Confirm').grid(row=3, column=0, sticky='E')

        ttk.Label(self, text='K').grid(row=0, column=3, sticky='W')
        ttk.Label(self, text='K/min').grid(row=1, column=3, sticky='W')

        # Spacer
        ttk.Label(self, text='  ').grid(row=0, column=1)
        self.grid_columnconfigure(1, weight=1) # Alows stretch and centering

        # Checkbuttons
        self.var_ramp = tk.BooleanVar(self)
        self.check_ramp = ttk.Checkbutton(self, variable=self.var_ramp)
        self.check_ramp.grid(row=2, column=2, columnspan=2)

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
        self.button_set = ttk.Button(self, text='Set T',
            command=self.Set, width=10)
        self.button_set.grid(row=3, column=2, columnspan=2)


    def Set(self):
        '''Confirms written values and sends to iTC'''
        values = [
            self.var_set.get(),
            self.var_rate.get(),
            'ON' if self.var_ramp.get() else 'OFF'
            ]
        logger.info('Setting iTC values: ' + str(values))
        self.ports.Set_Tset(self.parent.var_sens.get(), values)

    
    def Update(self, tset):
        '''Updates previously set values from iTC'''
        logger.info('Updating previous set temperature values: '+ str(tset))
        self.var_set.set(Strip_T(tset[0]))
        self.var_rate.set(Strip_T(tset[1]))
        self.var_ramp.set(True if tset[2] == 'ON' else False)



class Loop(tk.LabelFrame):
    '''Loop frame and inner objects'''
    def __init__(self, parent, ports):
        '''Calls init method of LabelFrame and fills up frame'''
        tk.LabelFrame.__init__(self, parent, text='Loop control', padx=10,
            pady=5)
        self.parent = parent
        self.ports = ports
        self.Widgets()


    def Widgets(self):
        '''Shapes the frame's widgets'''
        # Labels
        ttk.Label(self, text='P:').grid(row=0, column=0, sticky='E')
        ttk.Label(self, text='I:').grid(row=1, column=0, sticky='E')
        ttk.Label(self, text='D:').grid(row=2, column=0, sticky='E')
        ttk.Label(self, text='Heater').grid(row=3, column=0, sticky='E')
        ttk.Label(self, text='Aux').grid(row=4, column=0, sticky='E')

        ttk.Label(self, text='min').grid(row=1, column=3, sticky='W')
        ttk.Label(self, text='min').grid(row=2, column=3, sticky='W')

        # Spacer
        ttk.Label(self, text='  ').grid(row=0, column=1)
        self.grid_columnconfigure(1, weight=1) # Alows stretch and centering

        # Entries
        self.var_P = tk.StringVar(self)
        self.entry_P = ttk.Entry(self, width=7, textvariable=self.var_P,
            justify='right')
        self.entry_P.grid(row=0, column=2, sticky='E')

        self.var_I = tk.StringVar(self)
        self.entry_I = ttk.Entry(self, width=7, textvariable=self.var_I,
            justify='right')
        self.entry_I.grid(row=1, column=2, sticky='E')

        self.var_D = tk.StringVar(self)
        self.entry_D = ttk.Entry(self, width=7, textvariable=self.var_D,
            justify='right')
        self.entry_D.grid(row=2, column=2, sticky='E')

        # Combo box
        self.list_heat = List_sensors('HTR', self.ports.itc)
        self.var_heat = tk.StringVar(self)
        self.combo_heat = ttk.Combobox(self, width=8, state='readonly',
            values=self.list_heat, textvar=self.var_heat)
        self.combo_heat.grid(row=3, column=2, columnspan=2, sticky='W')

        self.list_aux = List_sensors('AUX', self.ports.itc)
        self.var_aux = tk.StringVar(self)
        self.combo_aux = ttk.Combobox(self, width=8, state='readonly',
            values=self.list_aux, textvar=self.var_aux)
        self.combo_aux.grid(row=4, column=2, columnspan=2, sticky='W')

        # Button
        self.button_set = ttk.Button(self, text='Set',
            command=self.Set, width=10)
        self.button_set.grid(row=5, column=0, columnspan=4)

    

    def Set(self):
        '''Confirms written values and sends to iTC'''
        logger.info('Updating loop parameters')


    def Update(self, tloop):
        '''Updates values from iTC'''
        logger.info('Updating loop control values: '+ str(tloop))
        self.var_P.set(tloop[0])
        self.var_I.set(tloop[1])
        self.var_D.set(tloop[2])
        self.var_heat.set(tloop[3])
        self.var_aux.set(tloop[4])



class Manual(tk.LabelFrame):
    '''Manual heater and flow control commands'''
    def __init__(self, parent, ports):
        '''Calls init method of LabelFrame and fills up frame'''
        tk.LabelFrame.__init__(self, parent, text='Manual control',
            padx=10, pady=5)
        self.parent = parent
        self.ports = ports
        self.Widgets()


    def Widgets(self):
        '''Shapes the frame's widgets'''
        # Labels
        ttk.Label(self, text='Heater %').grid(row=0, column=0)
        ttk.Label(self, text='Flow %').grid(row=0, column=2)

        # Spacer
        ttk.Label(self, text='  ').grid(row=0,column=1)
        self.grid_columnconfigure(1, weight=1) # Alows stretch and centering

        # Entries
        self.var_heater = tk.StringVar(self)
        self.entry_heater = ttk.Entry(self, textvariable=self.var_heater,
            justify='center', width=12)
        self.entry_heater.grid(row=1, column=0)

        self.var_flow = tk.StringVar(self)
        self.entry_flow = ttk.Entry(self, textvariable=self.var_flow,
            justify='center', width=12)
        self.entry_flow.grid(row=1, column=2)

        # Buttons
        self.button_heater_man = ttk.Button(self, text='Set heater',
            command=self.Set_heater, width=12)
        self.button_heater_man.grid(row=2, column=0)

        self.button_flow_man = ttk.Button(self, text='Set flow',
            command=self.Set_flow, width=12)
        self.button_flow_man.grid(row=2, column=2)

        self.button_heater_auto = ttk.Button(self, text='Auto heater',
            command=self.Auto_heater, width=12)
        self.button_heater_auto.grid(row=3, column=0)

        self.button_flow_auto = ttk.Button(self, text='Auto flow',
            command=self.Auto_flow, width=12)
        self.button_flow_auto.grid(row=3, column=2)

        # Check buttons
        self.var_heater_check = tk.BooleanVar(self)
        self.check_heater = ttk.Checkbutton(self, state='disabled',
            variable=self.var_heater_check)
        self.check_heater.grid(row=4, column=0)

        self.var_flow_check = tk.BooleanVar(self)
        self.check_flow = ttk.Checkbutton(self, state='disabled',
            variable=self.var_flow_check)
        self.check_flow.grid(row=4, column=2)


    def Set_heater(self):
        '''Confirms written values and sends to iTC'''
        # Get params
        sens = self.parent.var_sens.get()
        value = self.var_heater.get()
        # Log
        logger.info('Setting manual heater to '+value)
        # Change to manual (PID controll OFF)
        if self.ports.itc.__dict__[sens].Set_option('ENAB', 'OFF'):
            self.var_heater_check.set(False)
            # Set new value
            if not self.ports.itc.__dict__[sens].Set_option('HSET', value):
                logger.error('Failed to set heater to '+value)
        else: logger.error('Failed to disable PID control')


    def Set_flow(self):
        '''Confirms written values and sends to iTC'''
        # Get params
        sens = self.parent.var_sens.get()
        value = self.var_flow.get()
        # Log
        logger.info('Setting manual flow to: '+value)
        # Change to manual (flow control OFF)
        if self.ports.itc.__dict__[sens].Set_option('FAUT', 'OFF'):
            self.var_flow_check.set(False)
            # Set new value
            if not self.ports.itc.__dict__[sens].Set_option('FLSET', value):
                logger.error('Failed to set flow to '+value)
        else: logger.error('Failed to disable auto flow')


    def Auto_heater(self):
        '''Enables automatic heater control'''
        # get current sensor
        sens = self.parent.var_sens.get()
        # Log
        logger.info('Setting heater control to automatic')
        # Send to iTC, edit checkbox when sucessfull
        if self.ports.itc.__dict__[sens].Set_option('ENAB', 'ON'):
            self.var_heater_check.set(True)
        else: logger.error('Failed to enable auto heater control!')
        

    def Auto_flow(self):
        '''Enables automatic flow control'''
        # get current sensor
        sens = self.parent.var_sens.get()
        # Log
        logger.info('Setting flow control to automatic')
        # Send to iTC, edit checkbox when sucessfull
        if self.ports.itc.__dict__[sens].Set_option('FAUT', 'ON'):
            self.var_flow_check.set(True)
        else: logger.error('Failed to enable auto flow control!')


    def Update(self, tmanual):
        '''Updates values from iTC
            (heater, flow, heater_enable, flow_enable)'''
        logger.info('Updating manual control values'+ str(tmanual))
        self.var_heater.set(tmanual[0])
        self.var_flow.set(tmanual[1])
        self.var_heater_check.set(True if tmanual[2] == 'ON' else False)
        self.var_flow_check.set(True if tmanual[3] == 'ON' else False)



class Limits(tk.LabelFrame):
    '''Limits frame and inner objects'''
    def __init__(self, parent, ports):
        '''Calls init method of LabelFrame and fills up frame'''
        tk.LabelFrame.__init__(self, parent, text='Heating limits',
            padx=10, pady=5)
        self.parent = parent
        self.ports = ports
        self.Widgets()


    def Widgets(self):
        '''Shapes the frame's widgets'''
        # Labels
        ttk.Label(self, text='Heater limit:').grid(row=0, column=0, sticky='E')
        ttk.Label(self, text='Max temp limit:').grid(row=1, column=0,
            sticky='E')
        ttk.Label(self, text='Min temp limit:').grid(row=2, column=0,
            sticky='E')

        ttk.Label(self, text='V').grid(row=0, column=3, sticky='W')
        ttk.Label(self, text='K').grid(row=1, column=3, sticky='W')
        ttk.Label(self, text='K').grid(row=2, column=3, sticky='W')

        # Spacer
        ttk.Label(self, text='  ').grid(row=0, column=1)
        self.grid_columnconfigure(1, weight=1) # Alows stretch and centering

        # Entries
        self.var_heat = tk.StringVar(self)
        self.entry_heat = ttk.Entry(self, width=7, textvariable=self.var_heat,
            justify='right')
        self.entry_heat.grid(row=0, column=2)

        self.var_tmax = tk.StringVar(self)
        self.entry_tmax = ttk.Entry(self, width=7, textvariable=self.var_tmax,
            justify='right')
        self.entry_tmax.grid(row=1, column=2)

        self.var_tmin = tk.StringVar(self)
        self.entry_tmin = ttk.Entry(self, width=7, textvariable=self.var_tmin,
            justify='right')
        self.entry_tmin.grid(row=2, column=2)

        # Button
        self.button_set = ttk.Button(self, text='Set',
            command=self.Set, width=10)
        self.button_set.grid(row=4, column=0, columnspan=4)


    def Set(self):
        '''Confirms written values and sends to iTC'''
        logger.info('Setting heater limits')


    def Update(self, tlimits):
        '''Updates heating limits values from iTC'''
        logger.info('Updating heating limits values: '+ str(tlimits))
        self.var_heat.set(tlimits[0])
        self.var_tmax.set(Strip_T(tlimits[1]))
        self.var_tmin.set(Strip_T(tlimits[2]))


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
        ttk.Label(self, text='Sensor select').grid(row=0,
            column=0, sticky='E')

        # Spacer
        ttk.Label(self, text='  ').grid(row=0, column=1)
        self.grid_columnconfigure(1, weight=1) # Alows stretch and centering

        # Select sensor frame
        self.list_sens = List_sensors('TEMP', self.ports.itc)
        self.var_sens = tk.StringVar(self)
        #self.parent.var_sens = self.var_sens # give var_sens to itc frame
        self.var_sens.set(MAIN_SENSOR) # Default board
        self.combo_sens = ttk.Combobox(self, state='disabled',
            values=self.list_sens, textvar=self.var_sens, width=7)
        # Disabled to prevent tinkering, can change to 'readonly'
        self.combo_sens.grid(row=0, column=2)


