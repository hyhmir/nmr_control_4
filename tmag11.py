##############################################################################
#  class za upravljanje z tecmag softwerjem                                  #
##############################################################################

# uvozimo vse potrebne module
from numpy import fft
import time
import numpy as np
import matplotlib.pyplot as plt
from comtypes.client import CreateObject, GetActiveObject
import ctypes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from func11 import No_Sffx, To_Cpx, ReSize, BaselineCorr, LeftShift, MEAS_LOOP_TIME
import tkinter as tk
import os

# Refresh clock - can be set for quicker or slower refresh rate
# MEAS_LOOP_TIME = 0.1
dataylim = -100
dataYLIM = 100

fourierylim = -20000
fourierYLIM = 20000

class Tecmag():  # class ki komunicira z tnmr aplikacijo
    # Initialisation
    def __init__(self):
        self.Open_TNMR()
        self.params = {}
        self.nsc = 'NSC: N/A'
        self.linedatax = 'N/A'
        self.linefourx = 'N/A'
        self.eventx1 = 0  # Initialize eventx1
        self.eventx2 = 0  # Initialize eventx2
    
    # Access running TNMR window, if not active creates new TNMR window
    def Open_TNMR(self):
        try:
            self.doc = GetActiveObject('NTNMR.Document')
        except:
            self.doc = CreateObject('NTNMR.Document')

        try:
            self.app = GetActiveObject('NTNMR.Application')
            print('Found existing TNMR window')
        except OSError:
            self.app = CreateObject('NTNMR.Application')
            print('Opening new TNMR window')
            if self.app.CloseFile(''):
                pass
            else:
                print('Failed to close starting file')

    def set_params(self):
        self.params = {}
        self.params.update(self.dict_Acquisition)
        self.params.update(self.dict_Frequency)
        self.params.update(self.dict_Misc)
        self.params.update(self.dict_Sequence)

    def Parameter_setup(self, pulse=os.getcwd() + '\\pulse\\two_pulse.tps'):  # iz nastavljenega dashborda na tnmr ustvari tudi tu dashbord
        # pulse_path = 'D:\\TNMR\\sequences\\samo-test\\'  # treba sprement v gumb za search
        # pulse_file = 'samo-test.tps'
        print(pulse)
        self.app.LoadSequence(pulse)
        # self.doc.LoadSequence(pulse)

        self.app.ZG
        time.sleep(2)
        self.app.Abort
        # time.sleep(5)
        self.app.SaveParametersToFile(os.getcwd() + '\\bckfiles\\neki.txt')
        self.glavn_dikt = {}
        self.dict_Acquisition = {}
        self.dict_Frequency = {}
        self.dict_Processing = {}
        self.dict_GradPreemph = {}
        self.dict_B0Compensation = {}
        self.dict_Misc = {}
        self.dict_Display = {}
        self.dict_Sequence = {}
        self.slopar = {'Dwel Time':'DW', 'tau':'TAU', 'Acq.Points':'TD', 'Scans 1D':'NS', 'Actual Scans 1D':'NSC', 'Observe Freq.':'FR', 'd1':'D1','d2':'D2','d3':'D3','d4':'D4','d5':'D5','d6':'D6','d7':'D7','d8':'D8','d9':'D9',}
        self.sloadd = {'pulse':'PPFILE', 'Date':'DATESTA', 'Exp. Start Time':'TIMESTA', 'Exp. Finish Time':'TTIMEEND', 'a1':'a1','a123':'a123', 'a2':'a2', 'a3':'a3', 'atn1':'atn1', 'atn2':'atn2', 'Receiver Gain':'RecGain', 'Receiver Phase':'RecPh', 'Filter':'Filter', 'Pcryo':'Pcryo', 'ad':'ad'}
        self.slovar = {'_ITC_R0':1, '_ITC_R1':2, '_ITC_R2':3, '_ITC_W':4, '_ITC_NV':5}
        self.slovar1 = {'_FIELD':2}
        with open(os.getcwd() + '\\bckfiles\\neki.txt') as tekst:
            current = ''
            for line in tekst:
                if line != '\n':
                    if line[0] == ';':
                        current = line.replace(':', '').replace(';', '').replace(' ', '').replace('.', '').strip()
                    else:
                        if current == 'Acquisition':
                            if line == 'Grd. Orientation, \tXYZ\n':
                                current = ''
                            self.glavn_dikt.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'Frequency':
                            self.glavn_dikt.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'Processing':
                            self.glavn_dikt.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'GradPreemph':
                            self.glavn_dikt.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'B0Compensation':
                            self.glavn_dikt.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'Misc':
                            self.glavn_dikt.update({line.split(',')[0].strip():line.split(',')[-1].strip()})
                        if current == 'Display':
                            self.glavn_dikt.update({line.split(',')[0].strip():line.split(',')[1].strip()})
                        if current == 'Sequence':
                            self.glavn_dikt.update({line.split(',')[0].strip():line.split(',')[1].strip()})
        
        self.Get_parameterses()
        self.sequ = self.app.GetSequenceName

    def Runandsave(self, gui):  # pozene eksperiment in updatea slike in ostalo
        # print(self.params)
        for key, value in self.params.items():
            # time.sleep(1)
            try:
                self.doc.SetNMRParameter(key, value)
            except:
                pass

        print('Starting measurement')
        gui.update_paramis()
        self.doc.ZG()

        # Start the measurement loop
        while not self.app.CheckAcquisition:
            y11 = np.array(self.doc.Getdata[::2]) / int(self.app.GetNMRParameter('Actual Scans 1D'))
            y21 = np.array(self.doc.Getdata[1::2]) / int(self.app.GetNMRParameter('Actual Scans 1D'))
            self.data = y11 + 1.j * y21
            gui.UpdateFourier('lol')
            gui.acs.config(text=f"NSC: {self.app.GetNMRParameter('Actual Scans 1D')}/{self.app.GetNMRParameter('Scans 1D')}")
            gui.diks['Actual Scans 1D'].delete(0, tk.END)
            gui.diks['Actual Scans 1D'].insert(0, str(self.app.GetNMRParameter('Actual Scans 1D')))
            self.dict_Acquisition['Actual Scans 1D'] = str(self.app.GetNMRParameter('Actual Scans 1D'))
            time.sleep(MEAS_LOOP_TIME)
            # print(self.app.CheckAcqusition)

        gui.acs.config(text=f"NSC: {self.app.GetNMRParameter('Actual Scans 1D')}/{self.app.GetNMRParameter('Scans 1D')}")
        gui.diks['Actual Scans 1D'].delete(0, tk.END)
        gui.diks['Actual Scans 1D'].insert(0, str(self.app.GetNMRParameter('Actual Scans 1D')))
        self.dict_Acquisition['Actual Scans 1D'] = str(self.app.GetNMRParameter('Actual Scans 1D'))

        y11 = np.array(self.doc.Getdata[::2]) / int(self.app.GetNMRParameter('Actual Scans 1D'))
        y21 = np.array(self.doc.Getdata[1::2]) / int(self.app.GetNMRParameter('Actual Scans 1D'))
        self.data = y11 + 1.j * y21
        gui.UpdateFourier('lol')
        self.Get_parameters(gui)
        gui.update_paramis()
        print('Measurement finished')

    def Get_parameters(self, gui):  # iz tnmr aplikacije dobi podatke o casu eksperimenta
        start = self.app.GetNMRParameter('Exp. Start Time')[-8:]
        finish = self.app.GetNMRParameter('Exp. Finish Time')[-8:]
        date = self.app.GetNMRParameter('Date')
        date = '.'.join(reversed(date.split(' ')[0].split('/')))

        self.dict_Misc['Date'] = date
        self.dict_Misc['Exp. Start Time'] = start
        self.dict_Misc['Exp. Finish Time'] = finish
        self.dict_Misc['Temp.'] = gui.getT()

    def Get_parameterses(self):
        start = self.app.GetNMRParameter('Exp. Start Time')[-8:]
        finish = self.app.GetNMRParameter('Exp. Finish Time')[-8:]
        date = self.app.GetNMRParameter('Date')
        date = '.'.join(reversed(date.split(' ')[0].split('/')))

        self.dict_Misc['Date'] = date
        self.dict_Misc['Exp. Start Time'] = start
        self.dict_Misc['Exp. Finish Time'] = finish
