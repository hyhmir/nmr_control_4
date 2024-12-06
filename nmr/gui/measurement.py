'''Measurement overview frame'''

# Imports
import tkinter as tk    # Gui package
from tkinter import ttk # Fancier widgets
from tkinter import messagebox

import logging
logger = logging.getLogger('log')     # Set the logger



class Measurement_frame(tk.Frame):
    '''The Frame for selecting the type of measurement or starting new'''
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, width=1200, height=900, padx=5, pady=5)
        self.parent = parent

        self.Widgets()


    def Widgets(self):
        '''Shapes the frame's widgets'''
        # Title
        ttk.Label(self, text='Measurement').pack(side='top', padx=10)

        # Wrapper for subframes
        self.wrap_frame = tk.Frame(self)
        self.wrap_frame.pack(side='top', fill='both')

        # Type and control column
        self.type = Type(self)
        self.type.pack(side='left', fill='y')

        # Field column
        self.field = Parameter(self, 'Field')
        self.field.pack(side='left', fill='y')

        # Temperature column
        self.temperature = Parameter(self, 'Temperature')
        self.temperature.pack(side='left', fill='y')

        # Frequency column
        self.frequency = Parameter(self, 'Frequency')
        self.frequency.pack(side='top', fill='y')



class Type(tk.Frame):
    '''The frame for the measurement type and button column'''
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, width=300, height=900, padx=5, pady=5)
        self.parent = parent

        self.Widgets()


    def Widgets(self):
        '''Shapes the frame's widgets'''
        # Listbox for all measurement options
        self.listbox_measurements = tk.Listbox(self, exportselection=0, bd=5,
            relief='flat', height=14)
        self.listbox_measurements.pack(side='top', fill='both', pady=5)
        #self.listbox_measurements.bind('<Return>', self.Open_run)

        # Button view previous 
        self.button_open = ttk.Button(self, text='Open',
            command=self.Open_measurement)
        self.button_open.pack(side='top', fill='x', padx=5)


    def Open_measurement(self):
        pass



class Parameter(tk.Frame):
    '''Creates the skeleton for the selectable and listable parameters'''
    def __init__(self, parent, name):
        tk.Frame.__init__(self, parent, width=300, height=900, padx=5, pady=5)
        self.parent = parent
        
        # Title
        ttk.Label(self, text=name).pack(side='top', padx=10)

        # List of values
        self.listbox = tk.Listbox(self, exportselection=0, bd=5,
            relief='flat', height=14)
        self.listbox.pack(side='top', fill='both', pady=5)
        

