##############################################################################
#  class za upravljanje z graphic user interfaceom (gui)                     #
##############################################################################

# uvozimo vse potrebne module
import numpy as np
from numpy import fft
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
import os
import tkinter.messagebox as msgbox
from tmag11 import Tecmag
from func11 import *
from pytnt import TNTfile
from comtypes.client import CreateObject, GetActiveObject
import gui
import com
import logging
from gui.cryo import Cryo_application
from frames11 import *
import os

logger = logging.getLogger('log')

# Samo za nastavljanje visin crt in zacetnega obsega osi
dataylim = -100
dataYLIM = 100

fourierylim = -20000
fourierYLIM = 20000

class NMR_GUI(tk.Tk, Tecmag):
    '''Class for controling graphic user interface'''
    def __init__(self, tecmag, tmag):
        '''Initializes default GUI layout and inserts deafault parameters'''
        super().__init__()
        
        self.tecmag = tecmag
        self.tmag = tmag
        self.title("NMR Experiment Control")
        self.nsc = tecmag.nsc
        self.stevc = 1
        self.varclickxdata = tecmag.linedatax
        self.varclickxfour = tecmag.linefourx
        # self.line31 = None
        # self.line32 = None
        # self.line42 = None
        # self.dict_Acquisition = {}
        # self.dict_Frequency = {}
        # self.dict_Processing = {}
        # self.dict_GradPreemph = {}
        # self.dict_B0Compensation = {}
        # self.dict_Misc = {}
        # self.dict_Display = {}
        # self.dict_Sequence = {}
        self.protocol('WM_DELETE_WINDOW', self.Close_msg)

        logger.info('Starting main application Mercury_control')
        self.comports = com.ports.Ports()
        self.slopar = {'Dwel Time':'DW', 'tau':'TAU', 'Acq.Points':'TD', 'Scans 1D':'NS', 'Actual Scans 1D':'NSC', 'Observe Freq.':'FR', 'd1':'D1','d2':'D2','d3':'D3','d4':'D4','d5':'D5','d6':'D6','d7':'D7','d8':'D8','d9':'D9',}
        self.sloadd = {'File Name':'File Name', 'pulse':'PPFILE', 'Date':'DATESTA', 'Exp. Start Time':'TIMESTA', 'Exp. Finish Time':'TTIMEEND', 'a1':'a1','a123':'a123', 'a2':'a2', 'a3':'a3', 'atn1':'atn1', 'atn2':'atn2', 'Receiver Gain':'RecGain', 'Receiver Phase':'RecPh', 'Filter':'Filter', 'Pcryo':'Pcryo', 'ad':'ad'}
        self.slovar = {'_ITC_R0':1, '_ITC_R1':2, '_ITC_R2':3, '_ITC_W':4, '_ITC_NV':5}
        self.slovar1 = {'_FIELD':2}

####################################################################################################################
# Geometry manager
        width= self.winfo_screenwidth()               
        height= self.winfo_screenheight()
        self.geometry(f'{int(0.66 * width)}x{int(0.66 * height)}')

####################################################################################################################
# Tab Control
        tabControl = ttk.Notebook(self)
        self.tabControl = tabControl  # Store tabControl for use in update_tabs
        self.tab0 = ttk.Frame(tabControl)
        self.tab1 = ttk.Frame(tabControl)
        self.tab2 = ttk.Frame(tabControl)
        self.tab6 = ttk.Frame(tabControl)
        self.tab8 = ttk.Frame(tabControl)
        self.tab9 = ttk.Frame(tabControl)
        self.tab10 = ttk.Frame(tabControl)
        self.tab12 = ttk.Frame(tabControl)
        self.tab13 = ttk.Frame(tabControl)
        self.tab14 = ttk.Frame(tabControl)
        self.tab15 = ttk.Frame(tabControl)
        self.tab16 = ttk.Frame(tabControl)
        self.tab17 = ttk.Frame(tabControl)

        tabControl.add(self.tab0, text='File')
        tabControl.add(self.tab1, text='Acquisition')
        tabControl.add(self.tab2, text='Frequency')
        tabControl.add(self.tab6, text='Misc.')
        tabControl.add(self.tab8, text='Sequence')
        tabControl.add(self.tab9, text='Automatisation')
        tabControl.add(self.tab10, text='Fourier')
        tabControl.add(self.tab12, text='Temperature')
        tabControl.add(self.tab13, text='Sweep Experiment')
        tabControl.add(self.tab14, text='T1 Experiment')
        tabControl.add(self.tab15, text='T2 Experiment')
        tabControl.add(self.tab16, text='Cryo log')
        tabControl.add(self.tab17, text='Notification')

        tabControl.grid(row=0, column=0, columnspan=10, sticky="nsew")

        tabControl.bind("<<NotebookTabChanged>>", self.update_tabs)

####################################################################################################################
# Grid and column configurations
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        for i in range(18):
        # for i in range(8):
            tabControl.grid_columnconfigure(i, weight=1)
            tabControl.grid_rowconfigure(i, weight=1)

####################################################################################################################
# Tab 0 - File path
        self.diks = {}

        # tk.Label(self.tab0, text="File Path").grid(row=1, column=0, padx=10, pady=5)
        # self.entry_file_path = tk.Entry(self.tab0)
        # self.entry_file_path.insert(0, 'D:/TNMR/data/2024 Student')
        # self.entry_file_path.grid(row=1, column=1, padx=10, pady=5)
        self.browse_button = tk.Button(self.tab0, text="Load sequence", command=self.Load_sequence)
        self.browse_button.grid(row=1, column=0, padx=10, pady=5 , sticky='w')

        self.seq = tk.Label(self.tab0, text=self.tecmag.sequ)
        self.seq.grid(row=1, column=1, padx=10, pady=5 , sticky='w')

        self.openfile = tk.Button(self.tab0, text='Open file', command=self.open_file)
        self.openfile.grid(row=2, column=0, padx=10, pady=5, sticky='w')

        self.saveas = tk.Button(self.tab0, text='Save as', command=self.save_as)
        self.saveas.grid(row=3, column=0, padx=10, pady=5, sticky='w')

        self.saveastnt = tk.Button(self.tab0, text='Save .tnt', command=self.save_as_tnt)
        self.saveastnt.grid(row=3, column=1, padx=10, pady=5, sticky='w')

        self.opentnt = tk.Button(self.tab0, text='Open tnt', command=self.open_tnt)
        self.opentnt.grid(row=2, column=1, padx=10, pady=5, sticky='w')

####################################################################################################################
# Tab 1 - Acquisition
        self.dict_id_obfreq = {}
        self.dict_id_lasdel = {}
        self.dict_id_acqt = {}

        self.canvastab1 = tk.Canvas(self.tab1, height=50)
        self.canvastab1.grid(row=0, column=0, sticky="nsew")

        self.scroll1 = tk.Scrollbar(self.tab1, orient='horizontal', command=self.canvastab1.xview)
        self.scroll1.grid(row=1, column=0, sticky="ew")

        self.canvastab1.configure(xscrollcommand=self.scroll1.set)

        self.inner_frame1 = ttk.Frame(self.canvastab1, height=50)
        self.canvastab1.create_window((0, 0), window=self.inner_frame1, anchor='nw')

        self.inner_frame1.bind("<Configure>", lambda e: self.canvastab1.configure(scrollregion=self.canvastab1.bbox("all")))

        self.tab1.grid_rowconfigure(0, weight=1)
        self.tab1.grid_columnconfigure(0, weight=1)
        self.canvastab1.grid_rowconfigure(0, weight=1)
        self.canvastab1.grid_columnconfigure(0, weight=1)

        i = 0
        for key, value in tecmag.dict_Acquisition.items():
            tk.Label(self.inner_frame1, text=key).grid(row=i % 5, column=2*(i//5), padx=5, pady=0, sticky="w")
            self.diks[key] = tk.Entry(self.inner_frame1)
            self.diks[key].insert(0, value)
            self.diks[key].grid(row=i % 5, column=(2*(i//5) + 1), padx=5, pady=0, sticky="ew")
            self.diks[key].bind("<Return>", self.Focus)
            if key == 'Observe Freq.':
                self.dict_id_obfreq.update({1: self.diks[key]})
            if key == 'Acq. Time':
                self.dict_id_acqt.update({1: self.diks[key]})
            if key == 'Last Delay':
                self.dict_id_lasdel.update({1: self.diks[key]})
            i += 1

####################################################################################################################
# Tab 2 - Frequency
        self.canvastab2 = tk.Canvas(self.tab2, height=50)
        self.canvastab2.grid(row=0, column=0, sticky="nsew")

        self.scroll2 = tk.Scrollbar(self.tab2, orient='horizontal', command=self.canvastab2.xview)
        self.scroll2.grid(row=1, column=0, sticky="ew")

        self.canvastab2.configure(xscrollcommand=self.scroll2.set)

        self.inner_frame2 = ttk.Frame(self.canvastab2, height=50)
        self.canvastab2.create_window((0, 0), window=self.inner_frame2, anchor='nw')

        self.inner_frame2.bind("<Configure>", lambda e: self.canvastab2.configure(scrollregion=self.canvastab2.bbox("all")))

        self.tab2.grid_rowconfigure(0, weight=1)
        self.tab2.grid_columnconfigure(0, weight=1)
        self.canvastab2.grid_rowconfigure(0, weight=1)
        self.canvastab2.grid_columnconfigure(0, weight=1)

        i = 0
        for key, value in tecmag.dict_Frequency.items():
            tk.Label(self.inner_frame2, text=key).grid(row=i % 5, column=2*(i//5), padx=5, pady=0)
            self.diks[key] = tk.Entry(self.inner_frame2)
            self.diks[key].insert(0, value)
            self.diks[key].grid(row=i % 5, column=(2*(i//5) + 1), padx=5, pady=0)
            self.diks[key].bind("<Return>", self.Focus)
            if key == 'Observe Freq.':
                self.dict_id_obfreq.update({2: self.diks[key]})
            i += 1

####################################################################################################################
# Tab 6 - Misc
        self.canvastab6 = tk.Canvas(self.tab6, height=50)
        self.canvastab6.grid(row=0, column=0, sticky="nsew")

        self.scroll6 = tk.Scrollbar(self.tab6, orient='horizontal', command=self.canvastab6.xview)
        self.scroll6.grid(row=1, column=0, sticky="ew")

        self.canvastab6.configure(xscrollcommand=self.scroll6.set)

        self.inner_frame6 = ttk.Frame(self.canvastab6, height=50)
        self.canvastab6.create_window((0, 0), window=self.inner_frame6, anchor='nw')

        self.inner_frame6.bind("<Configure>", lambda e: self.canvastab6.configure(scrollregion=self.canvastab6.bbox("all")))

        self.tab6.grid_rowconfigure(0, weight=1)
        self.tab6.grid_columnconfigure(0, weight=1)
        self.canvastab6.grid_rowconfigure(0, weight=1)
        self.canvastab6.grid_columnconfigure(0, weight=1)

        i = 0
        for key, value in tecmag.dict_Misc.items():
            tk.Label(self.inner_frame6, text=key).grid(row=i % 5, column=2*(i//5), padx=5, pady=0)
            self.diks[key] = tk.Entry(self.inner_frame6)
            self.diks[key].insert(0, value)
            self.diks[key].grid(row=i % 5, column=(2*(i//5) + 1), padx=5, pady=0)
            self.diks[key].bind("<Return>", self.Focus)
            i += 1

####################################################################################################################
# Tab 8 - Sequence
        self.canvastab8 = tk.Canvas(self.tab8, height=50)
        self.canvastab8.grid(row=0, column=0, sticky="nsew")

        self.scroll8 = tk.Scrollbar(self.tab8, orient='horizontal', command=self.canvastab8.xview)
        self.scroll8.grid(row=1, column=0, sticky="ew")

        self.canvastab8.configure(xscrollcommand=self.scroll8.set)

        self.inner_frame8 = ttk.Frame(self.canvastab8, height=50)
        self.canvastab8.create_window((0, 0), window=self.inner_frame8, anchor='nw')

        self.inner_frame8.bind("<Configure>", lambda e: self.canvastab8.configure(scrollregion=self.canvastab8.bbox("all")))

        self.tab8.grid_rowconfigure(0, weight=1)
        self.tab8.grid_columnconfigure(0, weight=1)
        self.canvastab8.grid_rowconfigure(0, weight=1)
        self.canvastab8.grid_columnconfigure(0, weight=1)

        i = 0
        for key, value in tecmag.dict_Sequence.items():
            tk.Label(self.inner_frame8, text=key).grid(row=i % 5, column=2*(i//5), padx=5, pady=0)
            self.diks[key] = tk.Entry(self.inner_frame8)
            self.diks[key].insert(0, value)
            self.diks[key].grid(row=i % 5, column=(2*(i//5) + 1), padx=5, pady=0)
            self.diks[key].bind("<Return>", self.Focus)
            if key == 'Acq. Time':
                self.dict_id_acqt.update({2: self.diks[key]})
            if key == 'Last Delay':
                self.dict_id_lasdel.update({2: self.diks[key]})
            i += 1

####################################################################################################################
# Tab 9 - Automatisation
        dirlist = os.listdir(os.path.dirname(os.path.realpath(__file__)) + '\\skripte')
        self.izberi = tk.Listbox(self.tab9, selectmode=tk.SINGLE, height=5)
        for name in dirlist:
            if name != '__init__.py' and name != '__pycache__':
                self.izberi.insert(tk.END, name)

        self.izberi.grid(row=1, column=0, padx=10, pady=5, sticky='n')
        self.avtomat = tk.Button(self.tab9, text="run the script", command=self.avlt)
        self.avtomat.grid(row=2, column=0, padx=10, pady=5, sticky='s')

        self.avtoploti = tk.Label(self.tab9, text='N/A')
        self.avtoploti.grid(column=1, row=1)

####################################################################################################################
# Tab 10 - Fourier
        self.var1 = tk.IntVar()
        self.check1 = tk.Checkbutton(self.tab10, text='Auto phase correction', variable=self.var1, onvalue=True, offvalue=False, command=self.UpdateFourier)
        self.check1.grid(row=4, column=2, sticky='w')

        self.var2 = tk.IntVar()
        self.check2 = tk.Checkbutton(self.tab10,text='Full', variable=self.var2, onvalue=True, offvalue=False, command=self.UpdateFourier)
        self.check2.grid(row=3, column=2, sticky='w')

        tk.Label(self.tab10, text='Size').grid(row=1, column=0)
        self.size = tk.Entry(self.tab10)
        self.size.bind("<Return>", self.UpdateFourier)
        self.size.insert(0, self.diks['Acq. Points'].get())
        self.size.grid(row=1, column=1)

        tk.Label(self.tab10, text='Percent').grid(row=2, column=0)
        self.perc = tk.Entry(self.tab10)
        self.perc.bind("<Return>", self.UpdateFourier)
        self.perc.insert(0, '0')
        self.perc.grid(row=2, column=1)

        tk.Label(self.tab10, text='Index').grid(row=3, column=0)
        self.index = tk.Entry(self.tab10)
        self.index.bind("<Return>", self.UpdateFourier)
        self.index.insert(0, '0')
        self.index.grid(row=3, column=1)

        tk.Label(self.tab10, text='Phase Corr').grid(row=4, column=0)
        self.phc = tk.Entry(self.tab10)
        self.phc.bind("<Return>", self.UpdateFourier)
        self.phc.insert(0, '0')
        self.phc.grid(row=4, column=1)

        self.lower_bound = tk.Entry(self.tab10)
        self.lower_bound.insert(0, '0')
        self.lower_bound.bind("<Return>", self.UpdateFourier)
        self.lower_bound.grid(row=1, column=2)

        self.upper_bound = tk.Entry(self.tab10)
        self.upper_bound.insert(0, self.diks['Acq. Points'].get())
        self.upper_bound.bind("<Return>", self.UpdateFourier)
        self.upper_bound.grid(row=1, column=3)

        self.check_update_data = tk.IntVar()
        self.check_update_data_button = tk.Checkbutton(self.tab10, text='Update data plot', variable=self.check_update_data, onvalue=True, offvalue=False, command=self.UpdateFourier)
        self.check_update_data_button.grid(row=5, column=0)

        self.check_line = tk.IntVar()
        self.check_line_button = tk.Checkbutton(self.tab10, text='Sample spectre', variable=self.check_line, onvalue = True, offvalue = False, command=self.selectorspec)
        self.check_line_button.grid(row=1, column=5)

        self.check_linedat = tk.IntVar()
        self.check_linedat_button = tk.Checkbutton(self.tab10, text='Sample signal', variable=self.check_linedat, onvalue = True, offvalue = False, command=self.selectordat)
        self.check_linedat_button.grid(row=1, column=4)
        # self.check_linedat_button.select()

        self.opozorilo = tk.Label(self.tab10, text='', font=('TkDefaultFont', 20, 'bold'), fg='red', justify=tk.CENTER)
        self.opozorilo.grid(row=3, column=5, rowspan=3, columnspan=3)

####################################################################################################################
# Tab 12 - Temperature

        self.inner_frame12 = tk.Frame(self)
        gui.main.Main_application(self.inner_frame12, self.comports)

####################################################################################################################
# Tab 13 - Sweep Experiment
        tk.Label(self.tab13, text="Ime eksperimenta:").grid(row=0, column=0)
        self.sweep_name = tk.Entry(self.tab13)
        self.sweep_name.grid(row=0, column=1)

        tk.Label(self.tab13, text="Mapa eksperimenta:").grid(row=0, column=2)
        self.sweep_selected_directory = tk.Entry(self.tab13, text="N/A")
        self.sweep_selected_directory.grid(row=0, column=3)

        self.sweep_browse_directory = tk.Button(self.tab13, text="Browse", command=self.browse_file_sweep)
        self.sweep_browse_directory.grid(row=0, column=4)

        tk.Label(self.tab13, text='Min.').grid(row=1, column=0)
        self.sweepmin = tk.Entry(self.tab13)
        self.sweepmin.grid(row=1, column=1)
        self.sweepmin.bind('<Return>', self.Focus)

        tk.Label(self.tab13, text='Max.').grid(row=2, column=0)
        self.sweepmax = tk.Entry(self.tab13)
        self.sweepmax.grid(row=2, column=1)
        self.sweepmax.bind('<Return>', self.Focus)

        tk.Label(self.tab13, text='Interval').grid(row=3, column=0)
        self.sweepint = tk.Entry(self.tab13)
        self.sweepint.grid(row=3, column=1)
        self.sweepint.bind('<Return>', self.Focus)

        tk.Label(self.tab13, text='Integriraj (od/do):').grid(row=4, column=0)
        self.intodsw = tk.Entry(self.tab13)
        self.intdosw = tk.Entry(self.tab13)
        self.intodsw.grid(row=4, column=1)
        self.intdosw.grid(row=4, column=2)
        self.intodsw.bind('<Return>', self.Focus)
        self.intdosw.bind('<Return>', self.Focus)
        self.intodsw.insert(0, '0')
        self.intdosw.insert(0, self.tecmag.dict_Acquisition["Acq. Points"])

        tk.Label(self.tab13, text='Dodatne točke:').grid(row=3, column=2)
        self.sweeprep = tk.Entry(self.tab13)
        self.sweeprep.grid(row=3, column=3)
        self.sweeprep.bind('<Return>', self.Focus)

        self.start_sweep_repete = tk.Button(self.tab13, text='Dodaj', command=self.Start_Sweep_repete)
        self.start_sweep_repete.grid(row=3, column=4)

        self.start_sweep_experiment = tk.Button(self.tab13, text='Start', command=self.Start_Sweep_experiment)
        self.start_sweep_experiment.grid(row=5, column=0)

        self.current_freq = tk.Label(self.tab13, text='N/A')
        self.current_freq.grid(row=5, column=1)

####################################################################################################################
# Tab 14 - T1 Experiment
        tk.Label(self.tab14, text='min.').grid(row=0, column=0)
        tk.Label(self.tab14, text='Max.').grid(row=1, column=0)
        tk.Label(self.tab14, text='points').grid(row=2, column=0)
        tk.Label(self.tab14, text='repete').grid(row=2, column=2)
        tk.Label(self.tab14, text='Integriraj (od/do)').grid(row=0, column=2)

        self.current_d5 = tk.Label(self.tab14, text='N/A')
        self.current_d5.grid(row=3, column=1)

        self.T1mind5 = tk.Entry(self.tab14)
        self.T1maxd5 = tk.Entry(self.tab14)
        self.T1pts = tk.Entry(self.tab14)
        self.T1rep = tk.Entry(self.tab14)
        self.intodT1 = tk.Entry(self.tab14)
        self.intdoT1 = tk.Entry(self.tab14)

        self.varshuffleT1 = tk.IntVar()
        self.T1shuffle = tk.Checkbutton(self.tab14, text='Shuffle', variable=self.varshuffleT1, onvalue=True, offvalue=False)

        self.T1mind5.bind('<Return>', self.Focus)
        self.T1maxd5.bind('<Return>', self.Focus)
        self.T1pts.bind('<Return>', self.Focus)
        self.T1rep.bind('<Return>', self.Focus)

        self.T1mind5.grid(row=0, column=1)
        self.T1maxd5.grid(row=1, column=1)
        self.T1pts.grid(row=2, column=1)
        self.T1rep.grid(row=2, column=3)
        self.T1shuffle.grid(row=1, column=2)
        self.intodT1.grid(row=0, column=3)
        self.intdoT1.grid(row=0, column=4)

        self.intodT1.insert(0, '0')
        self.intdoT1.insert(0, '1024')

        self.start_T1_experiment = tk.Button(self.tab14, text='start', command=self.Start_T1_experiment)
        self.start_T1_experiment.grid(row=3, column=0)

        self.start_T1repete = tk.Button(self.tab14, text='dodaj', command=self.Start_T1_repete)
        self.start_T1repete.grid(row=2, column=4)

        tk.Label(self.tab14, text="Ime").grid(row=3, column=2)
        self.T1_name = tk.Entry(self.tab14)
        self.T1_name.grid(row=3, column=3)

        self.T1_browse_directory = tk.Button(self.tab14, text="Browse", command=self.browse_file_T1)
        self.T1_browse_directory.grid(row=3, column=4)
        self.T1_selected_directory = tk.Entry(self.tab14, text="N/A")
        self.T1_selected_directory.grid(row=3, column=5)

####################################################################################################################
# Tab 15 - T2 Experiment
        tk.Label(self.tab15, text='min.').grid(row=0, column=0)
        tk.Label(self.tab15, text='Max.').grid(row=1, column=0)
        tk.Label(self.tab15, text='interval').grid(row=2, column=0)
        tk.Label(self.tab15, text='repete').grid(row=2, column=2)
        tk.Label(self.tab15, text='Integriraj (od/do)').grid(row=0, column=2)

        self.current_tau = tk.Label(self.tab15, text='N/A')
        self.current_tau.grid(row=3, column=1)

        self.T2mind5 = tk.Entry(self.tab15)
        self.T2maxd5 = tk.Entry(self.tab15)
        self.T2int = tk.Entry(self.tab15)
        self.T2rep = tk.Entry(self.tab15)
        self.intodT2 = tk.Entry(self.tab15)
        self.intdoT2 = tk.Entry(self.tab15)

        self.varshuffleT2 = tk.IntVar()
        self.T2shuffle = tk.Checkbutton(self.tab15, text='Shuffle', variable=self.varshuffleT2, onvalue=True, offvalue=False)

        self.T2mind5.bind('<Return>', self.Focus)
        self.T2maxd5.bind('<Return>', self.Focus)
        self.T2int.bind('<Return>', self.Focus)
        self.T2rep.bind('<Return>', self.Focus)

        self.T2mind5.grid(row=0, column=1)
        self.T2maxd5.grid(row=1, column=1)
        self.T2int.grid(row=2, column=1)
        self.T2rep.grid(row=2, column=3)
        self.T2shuffle.grid(row=1, column=2)
        self.intodT2.grid(row=0, column=3)
        self.intdoT2.grid(row=0, column=4)

        self.intodT2.insert(0, '0')
        self.intdoT2.insert(0, '1024')

        self.start_T2_experiment = tk.Button(self.tab15, text='start', command=self.Start_T2_experiment)
        self.start_T2_experiment.grid(row=3, column=0)

        self.start_T2repete = tk.Button(self.tab15, text='dodaj', command=self.Start_T2_repete)
        self.start_T2repete.grid(row=2, column=4)

        tk.Label(self.tab15, text="Ime").grid(row=3, column=2)
        self.T2_name = tk.Entry(self.tab15)
        self.T2_name.grid(row=3, column=3)

        self.T2_browse_directory = tk.Button(self.tab15, text="Browse", command=self.browse_file_T2)
        self.T2_browse_directory.grid(row=3, column=4)
        self.T2_selected_directory = tk.Entry(self.tab15, text="N/A")
        self.T2_selected_directory.grid(row=3, column=5)

####################################################################################################################
# Tab 17 - Notificaton
        tk.Label(self.tab17, text="E-mail:").grid(row=0, column=0)
        self.user_mail = tk.Entry(self.tab17)
        self.user_mail.grid(row=0, column=1)
        self.user_mail.bind('<Return>', self.Focus)

        self.check_notify_var = tk.IntVar()
        self.check_notify = tk.Checkbutton(self.tab17, text="I want to be notified", onvalue=True, offvalue=False, variable=self.check_notify_var)
        self.check_notify.grid(row=0, column=2)

        tk.Label(self.tab17, text="Get notifications of:").grid(row=1, column=0)

        self.check_errors_var = tk.IntVar()
        self.check_errors = tk.Checkbutton(self.tab17, text="Errors", onvalue=True, offvalue=False, variable=self.check_errors_var)
        self.check_errors.grid(row=1, column=1)
        self.check_errors.select()

        self.check_finish_var = tk.IntVar()
        self.check_finish = tk.Checkbutton(self.tab17, text="Finish", onvalue=True, offvalue=False, variable=self.check_finish_var)
        self.check_finish.grid(row=1, column=2)
        self.check_finish.select()

        self.check_temperature_var = tk.IntVar()
        self.check_temperature = tk.Checkbutton(self.tab17, text="Temperature", onvalue=True, offvalue=False, variable=self.check_temperature_var)
        self.check_temperature.grid(row=1, column=3)
        self.check_temperature.select()


# Main frame initialization
        self.mainframe = tk.Frame()
        Main_frame(self, self.mainframe)

# Automatisation frame
        self.autoframe = tk.Frame()
        Automatisation_frame(self, self.autoframe)

# Sweep experiment frame
        self.sweepframe = tk.Frame()
        Sweep_frame(self, self.sweepframe)

# T1 experiment frame
        self.T1frame = tk.Frame()
        T1_frame(self, self.T1frame)

# T2 experiment frame
        self.T2frame = tk.Frame()
        T2_frame(self, self.T2frame)

####################################################################################################################
# Cryo application

        self.cryoframe = tk.Frame()
        self.cryoframe.grid_rowconfigure(0, weight=1)
        self.cryoframe.grid_columnconfigure(0, weight=1)
        #self.cryo_app = Cryo_application(self.cryoframe)

####################################################################################################################
# Main frame initialization and configuration
        self.mainframe.grid(row=1, column=0, sticky='nswe')

        self.mainframe.grid_columnconfigure(0, weight=1)
        self.mainframe.grid_columnconfigure(1, weight=1)
        self.mainframe.grid_rowconfigure(1, weight=1)
        # self.mainframe.grid_rowconfigure(2, weight=1)
####################################################################################################################
# Value binding

        self.dict_id_obfreq[1].bind("<Return>", self.setfreq1)

        self.dict_id_lasdel[1].bind("<Return>", self.setlasdel1)

        self.dict_id_obfreq[2].bind("<Return>", self.setfreq2)

        self.dict_id_lasdel[2].bind("<Return>", self.setlasdel2)

        self.diks['Dwell Time'].bind("<Return>", self.setacqtandsweepandpoints1dandfilter)

        self.diks['Acq. Points'].bind("<Return>", self.setacqtandsweepandpoints1dandfilter)

####################################################################################################################
# Called functions
    def browse_file_sweep(self):  # to funkcijo klicejo browse gumbi
        file_path = filedialog.askdirectory(initialdir=os.getcwd() + '\\exp')
        self.sweep_selected_directory.delete(0, tk.END)
        self.sweep_selected_directory.insert(0, file_path)

    def browse_file_T1(self):  # to funkcijo klicejo browse gumbi
        file_path = filedialog.askdirectory(initialdir=os.getcwd() + '\\exp')
        self.T1_selected_directory.delete(0, tk.END)
        self.T1_selected_directory.insert(0, file_path)

    def browse_file_T2(self):  # to funkcijo klicejo browse gumbi
        file_path = filedialog.askdirectory(initialdir=os.getcwd() + '\\exp')
        self.T2_selected_directory.delete(0, tk.END)
        self.T2_selected_directory.insert(0, file_path)

    def Focus(self, event):
        self.focus()
        for key, value in self.tecmag.dict_Acquisition.items():
            self.tecmag.dict_Acquisition[key] = self.diks[key].get()
        for key, value in self.tecmag.dict_Frequency.items():
            self.tecmag.dict_Frequency[key] = self.diks[key].get()
        for key, value in self.tecmag.dict_Misc.items():
            self.tecmag.dict_Misc[key] = self.diks[key].get()
        for key, value in self.tecmag.dict_Sequence.items():
            self.tecmag.dict_Sequence[key] = self.diks[key].get()

    def getT(self, hello=""):
        return str(self.comports.Get_T())

    def avlt(self):  # izvede izbrano skripto
        for i in self.izberi.curselection():
            a = __import__(str('skripte.' + (self.izberi.get(i).replace('.py', ''))), fromlist=[None])
            a.avto(self, self.tecmag)

    def stop_experiment(self):  # gumb
        self.tecmag.doc.Stop

    def abort_experiment(self):  # gumb
        self.tecmag.doc.Abort

    def selectordat(self):
        if self.check_line.get():
            self.check_line_button.deselect()
        self.UpdateFourier()

    def selectorspec(self):
        if self.check_linedat.get():
            self.check_linedat_button.deselect()
        self.UpdateFourier()

    def Autoscaledat(self):
        self.ax1.relim()
        self.ax1.autoscale(axis='x', tight=True)
        self.ax1.autoscale(axis='y')
        self.figure1.canvas.draw()

    def Autoscalefur(self):
        self.ax2.relim()
        self.ax2.autoscale(axis='x', tight=True)
        self.ax2.autoscale(axis='y')
        self.figure2.canvas.draw()

# Binding functions
    def setfreq1(self, event):  # ta in naslednje funkcije uskladijo parametre ki so med sabo povezani
        # self.focus()
        a = self.dict_id_obfreq[1].get()
        for value in self.dict_id_obfreq.values():
            value.delete(0, tk.END)
            value.insert(0, str(a))
        self.diks['F1 Freq.'].delete(0, tk.END)
        self.diks['F1 Freq.'].insert(0, str(a))
        self.tecmag.dict_Acquisition['Observe Freq.'] = self.dict_id_obfreq[1].get()
        self.tecmag.dict_Frequency['Observe Freq.'] = self.dict_id_obfreq[2].get()
        self.tecmag.dict_Frequency['F1 Freq.'] = self.diks['F1 Freq.'].get()
        self.focus()  # od fokusira iz widgeta

    def setlasdel1(self, event):
        # self.focus()
        a = self.dict_id_lasdel[1].get()
        for value in self.dict_id_obfreq.values():
            value.delete(0, tk.END)
            value.insert(0, str(a))
        self.tecmag.dict_Acquisition['Last Delay'] = self.dict_id_lasdel[1].get()
        self.tecmag.dict_Frequency['Observe Freq.'] = self.dict_id_lasdel[2].get()
        # self.tecmag.dict_Frequency['F1 Freq.'] = self.diks['F1 Freq.'].get()
        self.focus()

    def setfreq2(self, event):
        # self.focus()
        a = self.dict_id_obfreq[2].get()
        for value in self.dict_id_obfreq.values():
            value.delete(0, tk.END)
            value.insert(0, str(a))
        self.diks['F1 Freq.'].delete(0, tk.END)
        self.diks['F1 Freq.'].insert(0, str(a))
        self.tecmag.dict_Acquisition['Observe Freq.'] = self.dict_id_obfreq[1].get()
        self.tecmag.dict_Frequency['Observe Freq.'] = self.dict_id_obfreq[2].get()
        self.tecmag.dict_Frequency['F1 Freq.'] = self.diks['F1 Freq.'].get()
        self.focus()

    def setlasdel2(self, event):
        # self.focus()
        a = self.dict_id_lasdel[2].get()
        for value in self.dict_id_lasdel.values():
            value.delete(0, tk.END)
            value.insert(0, str(a))
        self.tecmag.dict_Acquisition['Last Delay'] = self.dict_id_lasdel[1].get()
        self.tecmag.dict_Sequence['Last Delay'] = self.dict_id_lasdel[2].get()
        self.focus()

    def setacqtandsweepandpoints1dandfilter(self, event):
        # self.focus()
        a = No_Sffx(self.diks['Dwell Time'].get()) * No_Sffx(self.diks['Acq. Points'].get())
        b = 1 / (2 * No_Sffx(self.diks['Dwell Time'].get()))
        for value in self.dict_id_acqt.values():
            value.delete(0, tk.END)
            value.insert(0, str(a))
        self.diks['SW +/-'].delete(0, tk.END)
        self.diks['SW +/-'].insert(0, str(b))
        self.diks['Points 1D'].delete(0, tk.END)
        self.diks['Points 1D'].insert(0, self.diks['Acq. Points'].get())
        self.diks['Filter'].delete(0, tk.END)
        self.diks['Filter'].insert(0, str(b))
        self.size.delete(0, tk.END)
        self.size.insert(0, self.diks['Acq. Points'].get())
        self.tecmag.dict_Acquisition['Acq. Points'] = self.diks['Acq. Points'].get()
        self.tecmag.dict_Acquisition['Points 1D'] = self.diks['Points 1D'].get()
        self.tecmag.dict_Acquisition['SW +/-'] = self.diks['SW +/-'].get()
        self.tecmag.dict_Acquisition['Filter'] = self.diks['Filter'].get()
        self.focus()

# Vertikalni crti
    def on_click1(self, event):
        if self.toolbar1.mode != 'pan/zoom' and self.toolbar1.mode != 'zoom rect':
            self.on_clicker1(event)

    def on_clicker1(self, event):
        if event.button == 1:
            if not self.check_linedat.get():
                if hasattr(self, 'line31') and self.line31:
                    self.line31.remove()
                if event.inaxes:
                    self.line31 = self.figure1.gca().axvline(x=event.xdata, color='k')
                else:
                    self.line31 = self.figure1.gca().axvline(x=0, color='k')

                self.linedatax1 = event.xdata
                self.xclickdata1.config(text=f'{round(self.linedatax1, 3)}')
                self.xclickindex11.config(text=f'{FromXtoIndexData(event.xdata, No_Sffx(self.diks['Dwell Time'].get()))}')
                self.canvas1.draw()
                self.UpdateFourier()

            if self.check_linedat.get():
                self.lower_bound.delete(0, tk.END)
                self.lower_bound.insert(0, str(FromXtoIndexData(event.xdata, No_Sffx(self.diks['Dwell Time'].get()))))
                if hasattr(self, 'line31') and self.line31:
                    self.line31.remove()
                if event.inaxes:
                    self.line31 = self.figure1.gca().axvline(x=event.xdata, color='k')
                else:
                    self.line31 = self.figure1.gca().axvline(x=0, color='k')

                self.linedatax1 = event.xdata
                self.xclickdata1.config(text=f'{round(self.linedatax1, 3)}')
                self.xclickindex11.config(text=f'{FromXtoIndexData(event.xdata, No_Sffx(self.diks['Dwell Time'].get()))}')
                self.canvas1.draw()
                self.UpdateFourier()

            self.intodsw.delete(0, tk.END)
            self.intodsw.insert(0, str(FromXtoIndexData(event.xdata, No_Sffx(self.diks['Dwell Time'].get()))))
            self.intodT1.delete(0, tk.END)
            self.intodT1.insert(0, str(FromXtoIndexData(event.xdata, No_Sffx(self.diks['Dwell Time'].get()))))
            self.intodT2.delete(0, tk.END)
            self.intodT2.insert(0, str(FromXtoIndexData(event.xdata, No_Sffx(self.diks['Dwell Time'].get()))))

        elif event.button == 3:
            if not self.check_linedat.get():
                if hasattr(self, 'line41') and self.line41:
                    self.line41.remove()
                if event.inaxes:
                    self.line41 = self.figure1.gca().axvline(x=event.xdata, color='k')
                else:
                    self.line41 = self.figure1.gca().axvline(x=0, color='k')

                self.linedatax2 = event.xdata
                self.xclickdata2.config(text=f'{round(self.linedatax2, 3)}')
                self.xclickindex12.config(text=f'{FromXtoIndexData(event.xdata, No_Sffx(self.diks['Dwell Time'].get()))}')
                self.canvas1.draw()
                self.UpdateFourier()

            if self.check_linedat.get():
                self.upper_bound.delete(0, tk.END)
                self.upper_bound.insert(0, str(FromXtoIndexData(event.xdata, No_Sffx(self.diks['Dwell Time'].get()))))
                if hasattr(self, 'line41') and self.line41:
                    self.line41.remove()
                if event.inaxes:
                    self.line41 = self.figure1.gca().axvline(x=event.xdata, color='k')
                else:
                    self.line41 = self.figure1.gca().axvline(x=0, color='k')

                self.linedatax2 = event.xdata
                self.xclickdata2.config(text=f'{round(self.linedatax2, 3)}')
                self.xclickindex12.config(text=f'{FromXtoIndexData(event.xdata, No_Sffx(self.diks['Dwell Time'].get()))}')
                self.canvas1.draw()
                self.UpdateFourier()

            self.intdosw.delete(0, tk.END)
            self.intdosw.insert(0, str(FromXtoIndexData(event.xdata, No_Sffx(self.diks['Dwell Time'].get()))))
            self.intdoT1.delete(0, tk.END)
            self.intdoT1.insert(0, str(FromXtoIndexData(event.xdata, No_Sffx(self.diks['Dwell Time'].get()))))
            self.intdoT2.delete(0, tk.END)
            self.intdoT2.insert(0, str(FromXtoIndexData(event.xdata, No_Sffx(self.diks['Dwell Time'].get()))))

    def on_click2(self, event):
        if self.toolbar2.mode != 'pan/zoom' and self.toolbar2.mode != 'zoom rect':
            self.on_clicker2(event)

    def on_clicker2(self, event):
        if event.button == 1:
            if not self.check_line.get():
                if hasattr(self, 'line32') and self.line32:
                    self.line32.remove()
                if event.inaxes:
                    self.line32 = self.figure2.gca().axvline(x=event.xdata, color='k')
                else:
                    self.line32 = self.figure2.gca().axvline(x=0, color='k')

                self.linefourx1 = event.xdata
                self.xclickfour1.config(text=f'{round(self.linefourx1, 3)}')
                self.xclickindex21.config(text=f'{FromXtoIndexFourier(event.xdata, No_Sffx(self.diks['Dwell Time'].get()), No_Sffx(self.size.get()))}')
                self.canvas2.draw()
                self.UpdateFourier()

            if self.check_line.get():
                self.lower_bound.delete(0, tk.END)
                self.lower_bound.insert(0, str(FromXtoIndexFourier(event.xdata, No_Sffx(self.diks['Dwell Time'].get()), No_Sffx(self.size.get()))))
                if hasattr(self, 'line32') and self.line32:
                    self.line32.remove()
                if event.inaxes:
                    self.line32 = self.figure2.gca().axvline(x=event.xdata, color='k')
                else:
                    self.line32 = self.figure2.gca().axvline(x=0, color='k')

                self.linefourx1 = event.xdata
                self.xclickfour1.config(text=f'{round(self.linefourx1, 3)}')
                self.xclickindex21.config(text=f'{FromXtoIndexFourier(event.xdata, No_Sffx(self.diks['Dwell Time'].get()), No_Sffx(self.size.get()))}')
                self.canvas2.draw()
                self.UpdateFourier()

        elif event.button == 3:
            if not self.check_line.get():
                if hasattr(self, 'line42') and self.line42:
                    self.line42.remove()
                if event.inaxes:
                    self.line42 = self.figure2.gca().axvline(x=event.xdata, color='k')
                else:
                    self.line42 = self.figure2.gca().axvline(x=0, color='k')

                self.linefourx2 = event.xdata
                self.xclickfour2.config(text=f'{round(self.linefourx2, 3)}')
                self.xclickindex22.config(text=f'{FromXtoIndexFourier(event.xdata, No_Sffx(self.diks['Dwell Time'].get()), No_Sffx(self.size.get()))}')
                self.canvas2.draw()
                self.UpdateFourier()

            if self.check_line.get():
                self.upper_bound.delete(0, tk.END)
                self.upper_bound.insert(0, str(FromXtoIndexFourier(event.xdata, No_Sffx(self.diks['Dwell Time'].get()), No_Sffx(self.size.get()))))
                if hasattr(self, 'line42') and self.line42:
                    self.line42.remove()
                if event.inaxes:
                    self.line42 = self.figure2.gca().axvline(x=event.xdata, color='k')
                else:
                    self.line42 = self.figure2.gca().axvline(x=0, color='k')

                self.linefourx2 = event.xdata
                self.xclickfour2.config(text=f'{round(self.linefourx2, 3)}')
                self.xclickindex22.config(text=f'{FromXtoIndexFourier(event.xdata, No_Sffx(self.diks['Dwell Time'].get()), No_Sffx(self.size.get()))}')
                self.canvas2.draw()
                self.UpdateFourier()

# File handling
    def save_as_tnt(self):
        file_type = [('TNT Files', '*.tnt')]
        file_saveas = filedialog.asksaveasfilename(filetypes=file_type, initialdir=os.getcwd() + '\\exp')
        if file_saveas == '' or file_saveas == None:
            return None
        self.tecmag.doc.SaveAs(file_saveas)

    def save_as(self):
        file_type = [('DAT Files', '*.dat')]
        file_saveas = filedialog.asksaveasfilename(filetypes=file_type, initialdir=os.getcwd() + '\\exp')
        if file_saveas == '' or file_saveas == None:
            return None
        file_saveas = file_saveas.replace('.dat', '')

        self.Write(file_saveas)

    def Load_sequence(self):
        file_type = [('TPS Files', '*.tps')]
        file_path = filedialog.askopenfilename(filetypes=file_type, initialdir=os.getcwd() + '\\pulse')
        if file_path == '' or file_path == None:
            return None
        print(file_path)
        file_path = file_path.replace('/', '\\\\')
        print(file_path)
        self.Load_sequenceer(file_path)
        print(os.getcwd())

    def Load_sequenceer(self, file_path):  # to funkcijo klicejo browse gumbi
        self.tecmag.dict_Acquisition = {}
        self.tecmag.dict_Frequency = {}
        self.tecmag.dict_Processing = {}
        self.tecmag.dict_GradPreemph = {}
        self.tecmag.dict_B0Compensation = {}
        self.tecmag.dict_Misc = {}
        self.tecmag.dict_Display = {}
        self.tecmag.dict_Sequence = {}
        # self.tecmag.app.LoadParameterSetupFromFile('D:\\TNMR\\setup\\dashboard\\test.txt')
        # file_path = filedialog.askopenfilename()
        # print(file_path)
        # file_path = file_path.replace('/', '\\\\')
        # print(file_path)
        self.tecmag.app.OpenFile(os.getcwd() + '\\bckfiles\\dummy.tnt')
        self.tecmag.app.LoadSequence(file_path)
        # # self.doc.LoadSequence(pulse)

        self.tecmag.app.ZG
        time.sleep(2)
        self.tecmag.app.Abort

        self.tecmag.app.SaveParametersToFile(os.getcwd() + '\\bckfiles\\load.txt')

        with open(os.getcwd() + '\\bckfiles\\load.txt') as tekst:
            current = ''
            for line in tekst:
                if line != '\n':
                    if line[0] == ';':
                        current = line.replace(':', '').replace(';', '').replace(' ', '').replace('.', '').strip()
                    else:
                        if current == 'Acquisition':
                            self.tecmag.dict_Acquisition.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'Frequency':
                            self.tecmag.dict_Frequency.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'Processing':
                            self.tecmag.dict_Processing.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'GradPreemph':
                            self.tecmag.dict_GradPreemph.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'B0Compensation':
                            self.tecmag.dict_B0Compensation.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'Misc':
                            self.tecmag.dict_Misc.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'Display':
                            self.tecmag.dict_Display.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'Sequence':
                            self.tecmag.dict_Sequence.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                            

        self.Update_GUI(self.tecmag.dict_Acquisition, self.tecmag.dict_Frequency, self.tecmag.dict_Misc, self.tecmag.dict_Sequence)

        self.size.delete(0, tk.END)
        self.size.insert(0, self.diks['Acq. Points'].get()) # da je updatean tudi ta
        # self.tecmag.app.SaveParameterSetupToFile('C:\\Users\\NMRSERVICE\\Desktop\\razclenjena_koda\\loadset.txt')
        print(self.tecmag.app.GetSequenceName)
        a = self.tecmag.app.GetSequenceName
        self.tecmag.app.CloseActiveFile
        self.tecmag.doc.LoadSequence(os.getcwd() + '\\pulse\\' + a + '.tps')
        self.seq.config(text=a)

    def open_tnt(self):
        self.tecmag.dict_Acquisition = {}
        self.tecmag.dict_Frequency = {}
        self.tecmag.dict_Processing = {}
        self.tecmag.dict_GradPreemph = {}
        self.tecmag.dict_B0Compensation = {}
        self.tecmag.dict_Misc = {}
        self.tecmag.dict_Display = {}
        self.tecmag.dict_Sequence = {}
        file_type = [('TNT Files', '*.tnt')]
        tnt_path = filedialog.askopenfilename(filetypes=file_type, initialdir=os.getcwd() + '\\exp')
        if tnt_path == '' or tnt_path == None:
            return None
        self.tecmag.app.OpenFile(tnt_path)
        tnt = TNTfile(tnt_path)
        podatki = tnt.DATA.T[:, 0].T[:, 0].T[0]
        paramdict = {}

        self.tecmag.app.SaveParametersToFile(os.getcwd() + '\\bckfiles\\temptnt.txt')

        with open(os.getcwd() + '\\bckfiles\\temptnt.txt') as tekst:
            current = ''
            for line in tekst:
                if line != '\n':
                    if line[0] == ';':
                        current = line.replace(':', '').replace(';', '').replace(' ', '').replace('.', '').strip()
                    else:
                        if current == 'Acquisition':
                            if line == 'Grd. Orientation, \tXYZ\n':
                                current = ''
                            self.tecmag.dict_Acquisition.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                            paramdict.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'Frequency':
                            self.tecmag.dict_Frequency.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                            paramdict.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'Processing':
                            self.tecmag.dict_Processing.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                            paramdict.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'GradPreemph':
                            self.tecmag.dict_GradPreemph.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                            paramdict.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'B0Compensation':
                            self.tecmag.dict_B0Compensation.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                            paramdict.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'Misc':
                            self.tecmag.dict_Misc.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                            paramdict.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'Display':
                            self.tecmag.dict_Display.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                            paramdict.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'Sequence':
                            self.tecmag.dict_Sequence.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                            paramdict.update({line.split(',')[0].strip():line.split(',')[1].strip()})

        self.tecmag.Get_parameterses()
        self.Update_GUI(self.tecmag.dict_Acquisition, self.tecmag.dict_Frequency, self.tecmag.dict_Misc, self.tecmag.dict_Sequence)

        self.size.delete(0, tk.END)
        self.size.insert(0, self.diks['Acq. Points'].get()) # da je updatean tudi ta
        print(self.tecmag.app.GetSequenceName)
        self.tecmag.doc.LoadSequence(os.getcwd() + '\\pulse\\' + self.tecmag.app.GetSequenceName + '.tps')

        acq = self.tecmag.dict_Acquisition

        podatki = podatki / int(acq['Actual Scans 1D'])
        self.tecmag.data = podatki

        if hasattr(self, 'line31'):
            self.line31.remove()
        self.line31 = self.figure1.gca().axvline(x=0)
        if hasattr(self, 'line32'):
            self.line32.remove()
        self.line32 = self.figure1.gca().axvline(x=0)
        if hasattr(self, 'line41'):
            self.line41.remove()
        self.line41 = self.figure1.gca().axvline(x=0)
        if hasattr(self, 'line42'):
            self.line42.remove()
        self.line42 = self.figure1.gca().axvline(x=0)
        self.UpdateFourier('lol')
        self.ax1.relim()
        self.ax1.autoscale(axis='x', tight=True)
        self.ax1.autoscale(axis='y')
        self.figure1.canvas.draw()
        self.ax2.relim()
        self.ax2.autoscale(axis='x', tight=True)
        self.ax2.autoscale(axis='y')
        self.figure2.canvas.draw()

        self.tecmag.app.CloseActiveFile
        a = self.tecmag.app.GetSequenceName
        self.seq.config(text=a)

    def Write(self, directory):  # zapise razultate                                              treba dodat da napise vse parametre ne sam tiste ki se setajo npr. pri avtomatizaciji
        # a = os.getcwd()
        a = directory
        a = a.replace('\\', '\\\\')
        params = self.read_paramis()
        # params.update(self.tecmag.dict_Acquisition)
        # params.update(self.tecmag.dict_Frequency)
        # params.update(self.tecmag.dict_Misc)
        # params.update(self.tecmag.dict_Sequence)
        tlog = ()
        flog = ()
        try:
            tlog = self.comports.Get_Tlog()
        except:
            pass
        try:
            flog = self.comports.Get_Flog()
        except:
            pass
        # tlog = self.comports.Get_Tlog()

        with open(a + '.dat', 'w', encoding='utf-8') as write_doc:

            write_doc.write('[PARAMETERS]\n')
            for key, value in self.slopar.items():
                try:
                    write_doc.write(str(value) + '=' + str(params[key]) + '\n')
                except:
                    pass

            write_doc.write('[ADDITIONAL]\n')
            for key, value in self.sloadd.items():
                try:
                    write_doc.write(str(value) + '=' + str(params[key]) + '\n')
                except:
                    pass

            write_doc.write('[VARIABLES]\n')
            for key, value in self.slovar.items():
                try:
                    write_doc.write(str(key) + '=' + str(tlog[value]) + '\n')
                except:
                    pass
            for key, value in self.slovar1.items():
                try:
                    write_doc.write(str(key) + '=' + str(flog[value]) + '\n')
                except:
                    pass

            write_doc.write('[PPFILE]\n')
            try:
                with open(os.getcwd() + '\\pulse\\exports\\' + str(self.seq.cget('text')) + '.txt', 'r', encoding='utf-8') as pulse:
                    index = 0
                    for vrstica in pulse:
                        if vrstica[0] == 'E':
                            index = 1
                            write_doc.write(vrstica)
                        elif index == 1:
                            write_doc.write(vrstica)
                        else:
                            pass
            except:
                pass

            write_doc.write('[DATA]\n')
            for i in range(0, int(len(self.tecmag.data)), 1):
                write_doc.write(f'{self.tecmag.data[i].real} {self.tecmag.data[i].imag}\n')

    def Write_integrals(self, directory, name, var, real, imag, control):
        directory = directory.replace('\\', '\\\\')
        with open(directory + "\\" + name + '.dat', 'w', encoding='utf-8') as write_doc:
            for i in range(0, len(var)):
                write_doc.write(str(var[i]) + "\t" + str(real[i]) + "\t" + str(imag[i]) + "\t" + str(np.sqrt(real[i] ** 2 + imag[i] ** 2)) + "\t" + str(control[i]) + "\n")

    def open_file(self):
        pulse = ''
        data = []
        # self.tecmag.dict_Acquisition = {}
        # self.tecmag.dict_Frequency = {}
        # self.tecmag.dict_Processing = {}
        # self.tecmag.dict_GradPreemph = {}
        # self.tecmag.dict_B0Compensation = {}
        # self.tecmag.dict_Misc = {}
        # self.tecmag.dict_Display = {}
        # self.tecmag.dict_Sequence = {}
        superdik = {}
        indikator = 0
        file_type = [('DAT Files', '*.dat')]
        file = filedialog.askopenfile(filetypes=file_type, initialdir=os.getcwd() + '\\exp')
        if file == '' or file == None:
            return None
        vrstice = file.readlines()
        for i in range(0, len(vrstice)):
            if indikator == 2 and vrstice[i] != '\n' and vrstice[i][0] != '[':
                par = Paramify(vrstice[i])
                self.tecmag.dict_Acquisition.update({par[0] : par[1]})
            if indikator == 3 and vrstice[i] != '\n' and vrstice[i][0] != '[':
                par = Paramify(vrstice[i])
                self.tecmag.dict_Frequency.update({par[0] : par[1]})
            if indikator == 4 and vrstice[i] != '\n' and vrstice[i][0] != '[' and vrstice[i][0] != 'T':
                par = Paramify(vrstice[i])
                self.tecmag.dict_Misc.update({par[0] : par[1]})
            if indikator == 5 and vrstice[i] != '\n' and vrstice[i][0] != '[' and vrstice[i][0] != 'D' and vrstice[i][0] != 'C':
                par = Paramify(vrstice[i])
                self.tecmag.dict_Sequence.update({par[0] : par[1]})
            if indikator == 1 and vrstice[i] != '\n' and vrstice[i][0] != '[':
                par = Numify(vrstice[i])
                data.append(float(par[0]) + 1.0j*float(par[1]))
            if indikator == 0 and vrstice[i] != '\n' and vrstice[i][0] != '[':
                par = Paramify(vrstice[i])
                superdik.update({par[0] : par[1]})
            if vrstice[i] == '[DATA]\n':
                indikator = 1
            if vrstice[i] == '[ACQUISITION]\n':
                indikator = 2
            if vrstice[i] == '[FREQUENCY]\n':
                indikator = 3
            if vrstice[i] == '[MISC.]\n':
                indikator = 4
            if vrstice[i] == '[SEQUENCE]\n':
                indikator = 5
            if vrstice[i][0] == 'D' or vrstice[i][0] == 'C':
                pulse = vrstice[i].strip('\n')
            if vrstice[i] == '[PPFILE]\n':
                indikator = 6
        
        pulse = superdik['PPFILE']
        self.Load_sequenceer(os.getcwd() + '\\pulse\\' + pulse + '.tps')
        # superdik['File Name'] = file.split('\\')[-1]
        # print(file.name)
        name = str(file.name).split('/')[-1]
        superdik['File Name'] = name

        for k, v in self.tecmag.dict_Acquisition.items():
            try:
                self.tecmag.dict_Acquisition[k] = superdik[self.slopar[k]]
            except:
                pass
            try:
                self.tecmag.dict_Acquisition[k] = superdik[self.sloadd[k]]
            except:
                pass
            try:
                self.tecmag.dict_Acquisition[k] = superdik[self.slovar[k]]
            except:
                pass

        for k, v in self.tecmag.dict_Sequence.items():
            try:
                self.tecmag.dict_Sequence[k] = superdik[self.slopar[k]]
            except:
                pass
            try:
                self.tecmag.dict_Sequence[k] = superdik[self.sloadd[k]]
            except:
                pass
            try:
                self.tecmag.dict_Sequence[k] = superdik[self.slovar[k]]
            except:
                pass

        for k, v in self.tecmag.dict_Misc.items():
            try:
                self.tecmag.dict_Misc[k] = superdik[self.slopar[k]]
            except:
                pass
            try:
                self.tecmag.dict_Misc[k] = superdik[self.sloadd[k]]
            except:
                pass
            try:
                self.tecmag.dict_Misc[k] = superdik[self.slovar[k]]
            except:
                pass

        for k, v in self.tecmag.dict_Frequency.items():
            try:
                self.tecmag.dict_Frequency[k] = superdik[self.slopar[k]]
            except:
                pass
            try:
                self.tecmag.dict_Frequency[k] = superdik[self.sloadd[k]]
            except:
                pass
            try:
                self.tecmag.dict_Frequency[k] = superdik[self.slovar[k]]
            except:
                pass

        # print(superdik)
        # print(self.tecmag.dict_Acquisition)
        self.Update_GUI(self.tecmag.dict_Acquisition, self.tecmag.dict_Frequency, self.tecmag.dict_Misc, self.tecmag.dict_Sequence)

        self.setfreq1('lol')

        self.size.delete(0, tk.END)
        self.size.insert(0, self.diks['Acq. Points'].get())

        self.tecmag.data = np.array(data)

        if hasattr(self, 'line31'):
            self.line31.remove()
        self.line31 = self.figure1.gca().axvline(x=0)
        if hasattr(self, 'line32'):
            self.line32.remove()
        self.line32 = self.figure1.gca().axvline(x=0)
        if hasattr(self, 'line41'):
            self.line41.remove()
        self.line41 = self.figure1.gca().axvline(x=0)
        if hasattr(self, 'line42'):
            self.line42.remove()
        self.line42 = self.figure1.gca().axvline(x=0)
        self.UpdateFourier('lol')
        self.ax1.relim()
        self.ax1.autoscale(axis='x', tight=True)
        self.ax1.autoscale(axis='y')
        self.figure1.canvas.draw()
        self.ax2.relim()
        self.ax2.autoscale(axis='x', tight=True)
        self.ax2.autoscale(axis='y')
        self.figure2.canvas.draw()

        print(pulse)
        self.tecmag.doc.LoadSequence(pulse)
        a = self.tecmag.app.GetSequenceName
        self.seq.config(text=a)

# Experiments
    def Start_Sweep_experiment(self):
        # self.Sweep_experiment(self.tecmag, self.figure1, self.figure2, self.acs, float(self.perc.get()), int(self.size.get()), int(self.index.get()), self.var2.get(), float(self.phc.get()), float(self.sweepmin.get()), float(self.sweepmax.get()), int(self.sweeppts.get()))
        sweep(self, self.figure4, os.getcwd() + '\\pulse\\two_pulse.tps', No_Sffx(self.sweepmin.get()), No_Sffx(self.sweepmax.get()), No_Sffx(self.sweepint.get()), self.current_freq, os.getcwd() + '\\exp', int(self.intodsw.get()), int(self.intdosw.get()))

    def Start_T1_experiment(self):
        T1(self, self.figure5, os.getcwd() + '\\pulse\\three_pulse.tps', No_Sffx(self.T1mind5.get()), No_Sffx(self.T1maxd5.get()), int(self.T1pts.get()), self.current_d5, os.getcwd() + '\\exp', int(self.intodT1.get()), int(self.intdoT1.get()))

    def Start_T2_experiment(self):
        T2(self, self.figure6, os.getcwd() + '\\pulse\\two_pulse.tps', No_Sffx(self.T2mind5.get()), No_Sffx(self.T2maxd5.get()), No_Sffx(self.T2int.get()), self.current_tau, os.getcwd() + '\\exp', int(self.intodT2.get()), int(self.intdoT2.get()))

    def Start_Sweep_repete(self):
        Sweeprepete(self, self.figure4, os.getcwd() + '\\pulse\\two_pulse.tps', No_Sffx(self.sweepmin.get()) - No_Sffx(self.sweepint.get()) + No_Sffx(self.sweepint.get())*np.floor((No_Sffx(self.sweepmax.get()) - No_Sffx(self.sweepmin.get()))/No_Sffx(self.sweepint.get())), No_Sffx(self.sweepint.get()), int(self.sweeprep.get()), self.current_freq, os.getcwd() + '\\exp', int(self.intodsw.get()), int(self.intdosw.get()))

    def Start_T1_repete(self):
        T1repete(self, self.figure5, os.getcwd() + '\\pulse\\three_pulse.tps', No_Sffx(self.T1maxd5.get()), (No_Sffx(self.T1maxd5.get())/No_Sffx(self.T1mind5.get()))**(1/(int(self.T1pts.get())-1)), int(self.T1rep.get()), self.current_d5, os.getcwd() + '\\exp', int(self.intodT1.get()), int(self.intdoT1.get()))

    def Start_T2_repete(self):
        T2repete(self, self.figure6, os.getcwd() + '\\pulse\\two_pulse.tps', No_Sffx(self.T2mind5.get()) + No_Sffx(self.T2int.get())*np.floor((No_Sffx(self.T2maxd5.get()) - No_Sffx(self.T2mind5.get()))/No_Sffx(self.T2int.get())), No_Sffx(self.T2int.get()), int(self.T2rep.get()), self.current_tau, os.getcwd() + '\\exp', int(self.intodT2.get()), int(self.intdoT2.get()))

# Message
    def Close_msg(self):
        '''Actions that happen when users presses x to close window'''
        msg = 'Are you sure you want to close the program?\n' \
              'Unsaved data will be lost!'
        if tk.messagebox.askokcancel('Quit', msg):
            logger.info('Main application closed')
            self.destroy() # Kills root

    def start_experiment(self):  # start experiment button (nastavi parametre, pozene eksperiment, zapise rezultate)
        self.tecmag.set_params()
        self.tecmag.Runandsave(self)
        # self.update_paramis()

    def Update_GUI(self, updated_Acquisition, updated_Frequency, updated_Misc, updated_Sequence):
        self.diks = {}
        # Update acquisition parameters
        for widget in self.inner_frame1.winfo_children():
            widget.destroy()

        i = 0
        for key, value in updated_Acquisition.items():
            tk.Label(self.inner_frame1, text=key).grid(row=i % 5, column=2*(i//5), padx=5, pady=0)
            self.diks[key] = tk.Entry(self.inner_frame1)
            self.diks[key].insert(0, value)
            self.diks[key].grid(row=i % 5, column=(2*(i//5) + 1), padx=5, pady=0)
            self.diks[key].bind("<Return>", self.Focus)
            if key == 'Observe Freq.':
                self.dict_id_obfreq.update({1: self.diks[key]})
            if key == 'Acq. Time':
                self.dict_id_acqt.update({1: self.diks[key]})
            if key == 'Last Delay':
                self.dict_id_lasdel.update({1: self.diks[key]})
            i += 1

        # Update frequency parameters
        for widget in self.inner_frame2.winfo_children():
            widget.destroy()

        i = 0
        for key, value in updated_Frequency.items():
            tk.Label(self.inner_frame2, text=key).grid(row=i % 5, column=2*(i//5), padx=5, pady=0)
            self.diks[key] = tk.Entry(self.inner_frame2)
            self.diks[key].insert(0, value)
            self.diks[key].grid(row=i % 5, column=(2*(i//5) + 1), padx=5, pady=0)
            self.diks[key].bind("<Return>", self.Focus)
            if key == 'Observe Freq.':
                self.dict_id_obfreq.update({2: self.diks[key]})
            i += 1

        # Update misc. parameters
        for widget in self.inner_frame6.winfo_children():
            widget.destroy()

        i = 0
        for key, value in updated_Misc.items():
            tk.Label(self.inner_frame6, text=key).grid(row=i % 5, column=2*(i//5), padx=5, pady=0)
            self.diks[key] = tk.Entry(self.inner_frame6)
            self.diks[key].insert(0, value)
            self.diks[key].grid(row=i % 5, column=(2*(i//5) + 1), padx=5, pady=0)
            self.diks[key].bind("<Return>", self.Focus)
            i += 1

        # Update sequence parameters
        for widget in self.inner_frame8.winfo_children():
            widget.destroy()

        i = 0
        for key, value in updated_Sequence.items():
            tk.Label(self.inner_frame8, text=key).grid(row=i % 5, column=2*(i//5), padx=5, pady=0)
            self.diks[key] = tk.Entry(self.inner_frame8)
            self.diks[key].insert(0, value)
            self.diks[key].grid(row=i % 5, column=(2*(i//5) + 1), padx=5, pady=0)
            self.diks[key].bind("<Return>", self.Focus)
            if key == 'Acq. Time':
                self.dict_id_acqt.update({2: self.diks[key]})
            if key == 'Last Delay':
                self.dict_id_lasdel.update({2: self.diks[key]})
            i += 1

        # Value binding (ker ustvarimo nove widgete)

        self.dict_id_obfreq[1].bind("<Return>", self.setfreq1)

        self.dict_id_lasdel[1].bind("<Return>", self.setlasdel1)

        self.dict_id_obfreq[2].bind("<Return>", self.setfreq2)

        self.dict_id_lasdel[2].bind("<Return>", self.setlasdel2)

        self.diks['Dwell Time'].bind("<Return>", self.setacqtandsweepandpoints1dandfilter)

        self.diks['Acq. Points'].bind("<Return>", self.setacqtandsweepandpoints1dandfilter)

    def update_tabs(self, event):
        # tab = event.widget.nametowidget(event.widget.select())  # get selected tab
        event.widget.configure(height=140)
        selected_tab = self.tabControl.index(self.tabControl.select())
        if selected_tab == 7:
            self.mainframe.grid_forget()
            self.autoframe.grid_forget()
            self.sweepframe.grid_forget()
            self.T1frame.grid_forget()
            self.T2frame.grid_forget()
            self.cryoframe.grid_forget()
            self.inner_frame12.grid(row=1, column=0, columnspan=6, sticky='nswe')
            event.widget.configure(height=20)

        elif selected_tab == 5:  # The index for 'Automatisation plots'
            self.mainframe.grid_forget()
            self.inner_frame12.grid_forget()
            self.sweepframe.grid_forget()
            self.T1frame.grid_forget()
            self.T2frame.grid_forget()
            self.cryoframe.grid_forget()
            self.autoframe.grid(row=1, column=0, sticky='nswe')
            event.widget.configure(height=130)

        elif selected_tab == 8:
            self.mainframe.grid_forget()
            self.inner_frame12.grid_forget()
            self.autoframe.grid_forget()
            self.T1frame.grid_forget()
            self.T2frame.grid_forget()
            self.cryoframe.grid_forget()
            self.sweepframe.grid(row=1, column=0, sticky='nswe')

        elif selected_tab == 9:
            self.mainframe.grid_forget()
            self.inner_frame12.grid_forget()
            self.autoframe.grid_forget()
            self.sweepframe.grid_forget()
            self.T2frame.grid_forget()
            self.cryoframe.grid_forget()
            self.T1frame.grid(row=1, column=0, sticky='nswe')

        elif selected_tab == 10:
            self.mainframe.grid_forget()
            self.inner_frame12.grid_forget()
            self.autoframe.grid_forget()
            self.sweepframe.grid_forget()
            self.T1frame.grid_forget()
            self.cryoframe.grid_forget()
            self.T2frame.grid(row=1, column=0, sticky='nswe')

        elif selected_tab == 11:
            self.mainframe.grid_forget()
            self.inner_frame12.grid_forget()
            self.autoframe.grid_forget()
            self.sweepframe.grid_forget()
            self.T1frame.grid_forget()
            self.T2frame.grid_forget()
            self.stevc = self.stevc+1
            self.cryoframe.grid(row=1, column=0, sticky='nswe')
            if self.stevc == 2:
                self.cryo_app = Cryo_application(self.cryoframe)

        else:
            self.autoframe.grid_forget()
            self.inner_frame12.grid_forget()
            self.sweepframe.grid_forget()
            self.T1frame.grid_forget()
            self.T2frame.grid_forget()
            self.cryoframe.grid_forget()
            self.mainframe.grid(row=1, column=0, sticky='nswe')

    def UpdateFourier(self, event="<Return>"): #for some ungodly reason sm rabu tuki podvojit ta shit če ne se ni izvedu. zakaj... nevem
        try:
            index = self.index.get()
            size = self.size.get()
            perc = self.perc.get()
            faza = self.phc.get()
            lowbound = self.lower_bound.get()
            upbound = self.upper_bound.get()
            # if self.index.get() != '' and self.size.get() != '' and self.perc.get() != '' and self.phc.get() != '' and self.lower_bound.get() != '' and self.upper_bound.get() != '':
            if self.index.get() == '':
                index = 0
            if self.size.get() == '':
                size = self.diks['Acq. Points'].get()
            if self.perc.get() == '':
                perc = 0
            if self.phc.get() == '':
                faza = 0
            if self.lower_bound.get() == '':
                lowbound = 0
            if self.upper_bound.get() == '':
                upbound = self.diks['Acq. Points'].get()
            self.UpdateFourierer(index, size, perc, faza, lowbound, upbound)
            self.opozorilo.config(text='')
        except:
            # print('error')
            self.UpdateFourierer(0, self.diks['Acq. Points'].get(), 0, 0, 0, self.diks['Acq. Points'].get())
            self.opozorilo.config(text='NEVELJAVEN VNOS!!!')

        try:
            index = self.index.get()
            size = self.size.get()
            perc = self.perc.get()
            faza = self.phc.get()
            lowbound = self.lower_bound.get()
            upbound = self.upper_bound.get()
            # if self.index.get() != '' and self.size.get() != '' and self.perc.get() != '' and self.phc.get() != '' and self.lower_bound.get() != '' and self.upper_bound.get() != '':
            if self.index.get() == '':
                index = 0
            if self.size.get() == '':
                size = self.diks['Acq. Points'].get()
            if self.perc.get() == '':
                perc = 0
            if self.phc.get() == '':
                faza = 0
            if self.lower_bound.get() == '':
                lowbound = 0
            if self.upper_bound.get() == '':
                upbound = self.diks['Acq. Points'].get()
            self.UpdateFourierer(index, size, perc, faza, lowbound, upbound)
            self.opozorilo.config(text='')
        except:
            # print('error')
            self.UpdateFourierer(0, self.diks['Acq. Points'].get(), 0, 0, 0, self.diks['Acq. Points'].get())
            self.opozorilo.config(text='NEVELJAVEN VNOS!!!')
            # tk.messagebox.showerror(title='Error', message='ú tweakin?')

    def UpdateFourierer(self, index, size, perc, faza, lowbound, upbound):
        data = self.tecmag.data
        data = BaselineCorr(data, float(perc))
        datareal = data.real
        dataimag = data.imag
        xdat = np.linspace(0, No_Sffx(self.diks['Dwell Time'].get()) * int(No_Sffx(self.diks['Acq. Points'].get())), int(No_Sffx(self.diks['Acq. Points'].get()))) * 1000
        x = np.linspace(0, No_Sffx(self.diks['Dwell Time'].get()) * int(size), int(size)) * 1000
        y1 = np.zeros(int(size))
        y2 = np.zeros(int(size))

        y1[0: len(datareal)] = datareal
        y2[0: len(dataimag)] = dataimag
        ym = np.sqrt(y1 ** 2 + y2 ** 2)
        
        # Figure za fouriera
        if hasattr(self, 'line12') and self.line12:
            self.line12.remove()
        if hasattr(self, 'line22') and self.line22:
            self.line22.remove()
        if hasattr(self, 'linefourmag') and self.linefourmag:
            self.linefourmag.remove()
        self.line12, = self.ax2.plot(x/1e10, y1/1e10, color='b')
        self.line22, = self.ax2.plot(x/1e10, y2/1e10, color='r')
        self.linefourmag, = self.ax2.plot(x/1e10, ym/1e10, color='g')
        self.line12.set_linewidth(0.3)
        self.line22.set_linewidth(0.3)
        self.linefourmag.set_linewidth(0.3)
        self.ax2.set_xlabel('freq [MHz]')
        # self.ax2.grid()

        signal_c = y1 + 1.j * y2
        spekter = fft.fft(LeftShift(ReSize(signal_c, int(size)), int(index), self.var2.get()))
        freq = np.linspace(-1/(2E6*No_Sffx(self.diks['Dwell Time'].get())), 1/(2E6*No_Sffx(self.diks['Dwell Time'].get())), int(size))
        y12 = np.zeros(int(size))
        y12[0:int(int(size)/2)] = spekter.real.T[int(int(size)/2):] 
        y12[int(int(size)/2):] = spekter.real.T[0:int(int(size)/2)]
        y22 = np.zeros(int(size))
        y22[0:int(int(size)/2)] = spekter.imag.T[int(int(size)/2):] 
        y22[int(int(size)/2):] = spekter.imag.T[0:int(int(size)/2)]

        if self.var1.get():
            phc = 0
            if self.check_linedat.get():
                phc = np.arctan(Integrate(y2, int(lowbound), int(upbound)) / Integrate(y1, int(lowbound), int(upbound)))
            elif self.check_line.get():
                phc = np.arctan(Integrate(y22, int(lowbound), int(upbound)) / Integrate(y12, int(lowbound), int(upbound)))  # za dodat start stop argumente
            phc = -np.rad2deg(phc)
            self.phc.delete(0, tk.END)
            self.phc.insert(0, str(phc))
        
        signal_c = signal_c * np.exp(1.j * np.deg2rad(float(faza)))
        spekter = fft.fft(LeftShift(ReSize(signal_c, int(size)), int(index), self.var2.get()))
        freq = np.linspace(-1/(2E6*No_Sffx(self.diks['Dwell Time'].get())), 1/(2E6*No_Sffx(self.diks['Dwell Time'].get())), int(size))
        y12 = np.zeros(int(size))
        y12[0:int(int(size)/2)] = spekter.real.T[int(int(size)/2):] 
        y12[int(int(size)/2):] = spekter.real.T[0:int(int(size)/2)]
        y22 = np.zeros(int(size))
        y22[0:int(int(size)/2)] = spekter.imag.T[int(int(size)/2):] 
        y22[int(int(size)/2):] = spekter.imag.T[0:int(int(size)/2)]
        yfourmag = np.sqrt(y12 ** 2 + y22 ** 2)

        if self.check_real_var.get():
            self.line12.set_xdata(-freq)
            self.line12.set_ydata(y12)

        if self.check_imag_var.get():
            self.line22.set_xdata(-freq)
            self.line22.set_ydata(y22)

        if self.check_magn_var.get():
            self.linefourmag.set_xdata(-freq)
            self.linefourmag.set_ydata(yfourmag)

        self.figure2.canvas.draw()
        self.figure2.canvas.flush_events()
        # self.focus()

        if self.check_update_data.get():
            # Figure za dataplot
            if hasattr(self, 'line11') and self.line11:
                self.line11.remove()
            if hasattr(self, 'line21') and self.line21:
                self.line21.remove()
            if hasattr(self, 'linedatamag') and self.linedatamag:
                self.linedatamag.remove()
            self.line11, = self.ax1.plot(x, y1/1e10, color='b')
            self.line21, = self.ax1.plot(x, y2/1e10, color='r')
            self.linedatamag, = self.ax1.plot(x, ym/1e10, color='g')
            self.line11.set_linewidth(0.3)
            self.line21.set_linewidth(0.3)
            self.linedatamag.set_linewidth(0.3)
            self.ax1.set_xlabel('time [ms]')

            # PHC dataplot
            data_phc = data * np.exp(1.j * np.deg2rad(float(faza)))
            y11 = np.array(data_phc.real)
            y21 = np.array(data_phc.imag)
            ymag = np.sqrt(y11 ** 2 + y21 ** 2)
            
            if self.check_real_var.get():
                self.line11.set_xdata(xdat)
                self.line11.set_ydata(y11)

            if self.check_imag_var.get():
                self.line21.set_xdata(xdat)
                self.line21.set_ydata(y21)
            
            if self.check_magn_var.get():
                self.linedatamag.set_xdata(xdat)
                self.linedatamag.set_ydata(ymag)

            self.figure1.canvas.draw()
            self.figure1.canvas.flush_events()
            # self.focus()
        
        else:
            # Figure za dataplot
            if hasattr(self, 'line11') and self.line11:
                self.line11.remove()
            if hasattr(self, 'line21') and self.line21:
                self.line21.remove()
            if hasattr(self, 'linedatamag') and self.linedatamag:
                self.linedatamag.remove()

            self.line11, = self.ax1.plot(x, y1/1e10, color='b')
            self.line21, = self.ax1.plot(x, y2/1e10, color='r')
            self.linedatamag, = self.ax1.plot(x, ym/1e10, color='g')
            self.line11.set_linewidth(0.3)
            self.line21.set_linewidth(0.3)
            self.linedatamag.set_linewidth(0.3)
            self.ax1.set_xlabel('time [ms]')

            # PHC dataplot
            data_phc = data
            y11 = np.array(data_phc.real)
            y21 = np.array(data_phc.imag)
            ymag = np.sqrt(y11 ** 2 + y21 ** 2)

            if self.check_real_var.get():
                self.line11.set_xdata(xdat)
                self.line11.set_ydata(y11)

            if self.check_imag_var.get():
                self.line21.set_xdata(xdat)
                self.line21.set_ydata(y21)

            if self.check_magn_var.get():
                self.linedatamag.set_xdata(xdat)
                self.linedatamag.set_ydata(ymag)

            self.figure1.canvas.draw()
            self.figure1.canvas.flush_events()
            # self.focus()
        self.focus

    def read_paramis(self):
        params = {}

        for key, value in self.tecmag.dict_Acquisition.items():
            params[key] = self.diks[key].get()

        for key, value in self.tecmag.dict_Frequency.items():
            params[key] = self.diks[key].get()

        for key, value in self.tecmag.dict_Misc.items():

            params[key] = self.diks[key].get()

        for key, value in self.tecmag.dict_Sequence.items():
            params[key] = self.diks[key].get()

        if not all(params.values()):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        params['temp'] = self.getT()
        params['pulse'] = self.seq.cget('text')
        return params

    def update_paramis(self):
        for key, value in self.tecmag.dict_Acquisition.items():
            self.tecmag.dict_Acquisition[key] = self.tecmag.doc.GetNMRParameter(str(key))

        for key, value in self.tecmag.dict_Frequency.items():
            self.tecmag.dict_Frequency[key] = self.tecmag.doc.GetNMRParameter(str(key))

        for key, value in self.tecmag.dict_Misc.items():
            if key != 'Temp.' and key != 'Date' and key !='Exp. Finish Time' and key !='Exp. Start Time':
                self.tecmag.dict_Misc[key] = self.tecmag.doc.GetNMRParameter(str(key))

        for key, value in self.tecmag.dict_Sequence.items():
            self.tecmag.dict_Sequence[key] = self.tecmag.doc.GetNMRParameter(str(key))

        self.Update_GUI(self.tecmag.dict_Acquisition, self.tecmag.dict_Frequency, self.tecmag.dict_Misc, self.tecmag.dict_Sequence)
