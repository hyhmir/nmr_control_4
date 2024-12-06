'''Experiment select frame'''

# Imports
import tkinter as tk    # Gui package
from tkinter import ttk # Fancier widgets
from tkinter import messagebox

import logging
logger = logging.getLogger('log')     # Set the logger



class Experiment_frame(tk.Frame):
    '''The Frame for selecting experiments or creating new'''
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, width=300, height=900, padx=5, pady=5)
        self.parent = parent

        self.Widgets()


    def Widgets(self):
        '''Shapes the frame's widgets'''
        # Label
        self.label_title = ttk.Label(self, text='Experiments')
        #self.label_title.config(font=('Courier', 16))
        self.label_title.pack(side='top', padx=10)

        # Entry new experiment
        self.var_new = tk.StringVar(self)
        self.entry_new = ttk.Entry(self, textvariable=self.var_new)
        self.entry_new.pack(side='top', pady=5, padx=5)
        self.entry_new.bind('<Return>', self.New_experiment)

        # Button new experiment
        self.button_new = ttk.Button(self, text='Create New',
            command=self.New_experiment)
        self.button_new.pack(side='top', fill='x', padx=5)

        # Listbox for all existing experiments
        self.listbox_experiments = tk.Listbox(self, exportselection=0, bd=5,
            relief='flat', height=20)
        self.listbox_experiments.pack(side='top', fill='both', pady=5)
        self.listbox_experiments.bind('<Return>', self.Open_experiment)

        # Button open experiment
        self.button_open = ttk.Button(self, text='Open',
            command=self.Open_experiment)
        self.button_open.pack(side='top', fill='x', padx=5)
        

    def New_experiment(self, event=None):
        '''Creates new experiment entry and the directories'''
        print(event)


    def Open_experiment(self, event=None):
        '''Opens the selected experiment'''
        print(event)


