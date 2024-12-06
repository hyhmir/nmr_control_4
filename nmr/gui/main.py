'''Top level window of TNMR_gui application'''

# Imports
import tkinter as tk    # Gui package
#from tkinter import ttk # Fancier widgets

#import logging
#logger = logging.getLogger('log')    # Set the logger

from nmr.gui.experiment import Experiment_frame
from nmr.gui.run import Run_frame
from nmr.gui.measurement import Measurement_frame



class TNMR_application(tk.Frame):
    '''Toplevel window holding the skeleton for NMR operations'''
    def __init__(self, parent):
        '''Initialize the Toplevel frame'''

        self.parent = parent
        self.parent.wm_title('GUI for NMR control')
        self.parent.minsize(height=768, width=1024)
        #self.parent.title('NTNMR_application')
        
        # Creates the popup window as self
        tk.Frame.__init__(self, parent, height=900, width=1600)
        self.pack(fill='both', expand=True)

        self.Add_frames()


    def Add_frames(self):
        '''Packs the frames and positions them'''
        self.experiment_frame=Experiment_frame(self)
        self.experiment_frame.pack(side='left', fill='y')

        self.run_frame=Run_frame(self)
        self.run_frame.pack(side='left', fill='y')

        self.measurement_frame=Measurement_frame(self)
        self.measurement_frame.pack(side='left', fill='y')