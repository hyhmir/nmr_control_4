'''Run select/create frame'''

# Imports
import tkinter as tk    # Gui package
from tkinter import ttk # Fancier widgets
from tkinter import messagebox

import logging
logger = logging.getLogger('log')     # Set the logger



class Run_frame(tk.Frame):
    '''The Frame for selecting runs or creating new'''
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, width=300, height=900, padx=5, pady=5)
        self.parent = parent

        self.Widgets()


    def Widgets(self):
        '''Shapes the frame's widgets'''
        # Label
        #self.label_title = ttk.Label(self, text='Run')
        #self.label_title.config(font=('Courier', 16))
        #self.label_title.pack(side='top', padx=10)
        ttk.Label(self, text='Run').pack(side='top', padx=10)

        # Entry new run
        self.var_new = tk.StringVar(self)
        self.entry_new = ttk.Entry(self, textvariable=self.var_new)
        self.entry_new.pack(side='top', pady=5, padx=5)
        self.entry_new.bind('<Return>', self.New_run)

        # Button new experiment
        self.button_new = ttk.Button(self, text='Create New',
            command=self.New_run)
        self.button_new.pack(side='top', fill='x', padx=5)

        # Listbox for all existing experiments
        self.listbox_runs = tk.Listbox(self, exportselection=0, bd=5,
            relief='flat', height=14)
        self.listbox_runs.pack(side='top', fill='both', pady=5)
        self.listbox_runs.bind('<Return>', self.Open_run)

        # Button open experiment
        self.button_open = ttk.Button(self, text='Open',
            command=self.Open_run)
        self.button_open.pack(side='top', fill='x', padx=5)

        # Comment label
        ttk.Label(self, text='Comments:').pack(side='top', padx=10, pady=5)

        # Comment textbox
        self.var_comment = tk.StringVar(self)
        self.text_comment = tk.Text(self, relief='flat', height=8, width=10)
        self.text_comment.pack(side='top', fill='x', padx=5)
        

    def New_run(self, event=None):
        '''Creates new run entry and the directories'''
        pass


    def Open_run(self, event=None):
        '''Opens the selected run'''
        pass


