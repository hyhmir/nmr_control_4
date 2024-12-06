'''Main window of gui application'''

# Imports
import tkinter as tk    # Gui package
#from tkinter import ttk # Fancier widgets
from tkinter import messagebox

from gui.itc import ITC_frame
from gui.ips import IPS_frame
from gui.log import Log_frame

import logging
logger = logging.getLogger('log')     # Set the logger
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S") # Better logging format. Most importantly, it shows the timestamp.
# The file and linenumber is also shown.

# Popup windows
from nmr.gui import main
from gui.cryo import Cryo_application



class Main_application(tk.Frame):
    '''Main frame holding the skeleton for all future frames'''
    def __init__(self, parent, ports):
        '''Initializes the skeleton frame into "self"'''
        self.ports = ports
        # Edits root
        self.parent = parent
        #self.parent.wm_title('GUI for iTC and iPC control')
        #self.parent.protocol('WM_DELETE_WINDOW', self.On_close)
        #self.parent.minsize(height=768, width=1024)

        # Creates main frame as self
        self.Find_resolution()
        tk.Frame.__init__(self, parent, height=900, width=1600)
        # Allows stretching
        self.pack(fill='both', expand=True)

        #self.Add_menu()
        self.Add_frames()


    def Add_frames(self):
        '''Packs the inside frames'''
        # Use pack for expandable slots, grid for fixed sizes
        # Check if devices exist!
        if self.ports.itc != None:
            self.itc_frame=ITC_frame(self, self.ports)
            self.itc_frame.pack(side='left', fill='y')
            #self.itc_frame.grid(column=0, row=0)

        if self.ports.ips != None:
            self.ips_frame=IPS_frame(self, self.ports)
            self.ips_frame.pack(side='right', fill='y')
            #self.ips_frame.grid(column=2, row=0)

        self.log_frame = Log_frame(self, self.ports)
        self.log_frame.pack(side='left', expand=True, fill='both')
        #self.log_frame.grid(column=1, row=0)


    def Add_menu(self):
        '''Creates the window menu'''
        self.menu = Menu(self.parent)
        self.parent.config(menu=self.menu)


    def Find_resolution(self):
        '''Finds computer's resolution'''
        self.screen_width = self.parent.winfo_screenwidth()
        self.screen_height = self.parent.winfo_screenheight()

    
    def On_close(self):
        '''Actions that happen when users presses x to close window'''
        msg = 'Are you sure you want to close the program?\n' \
              'Unsaved data will be lost!'
        if tk.messagebox.askokcancel('Quit', msg):
            logger.info('Main application closed')
            self.parent.destroy() # Kills root



class Menu(tk.Menu):
    '''Creates the top window menu in root'''
    def __init__(self, root):
        '''Initializes as menu class'''
        tk.Menu.__init__(self, root)
        self.root = root

        # File cascade
        self.file = tk.Menu(self, tearoff=0)
        self.file.add_command(label='Exit without saving',
            command=root.destroy)
        self.file.add_command(label='Open TNMR application',
            command=self.Run_TNMR)
        self.file.add_command(label='Plot cryogen log',
            command=self.Run_cryo)
        self.add_cascade(label='File', menu=self.file)

        # Cryo log option
        self.add_command(label='Cryo log', command=self.Run_cryo)


    def Run_TNMR(self):
        '''Opens the TNMR application in separate window'''
        TNMR_window = tk.Toplevel(self.root, height=900, width=1600)
        main.TNMR_application(TNMR_window)


    def Run_cryo(self):
        '''Opens cyogen log in separate window'''
        cryo_window = tk.Toplevel(self.root)
        self.cryo_app = Cryo_application(cryo_window)



def Error_incomplete():
    '''Warns user that content is not fully implemented'''
    tk.messagebox.showerror('Error', 'The function is not yet implemented')



if __name__ == '__main__':
    #get it running
    pass


