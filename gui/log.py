'''Log frame'''

# Imports
import tkinter as tk    # Gui package
from tkinter import ttk # Fancier widgets
from tkinter import messagebox
from tkinter import simpledialog # for string query, etc
# Plotting
import matplotlib
matplotlib.use('TkAgg') # Selects tkinter backend
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
    NavigationToolbar2Tk)
from matplotlib.figure import Figure
# Logging
import datetime # A format for dates and time
import csv      # For importing and exporting CSV files
import os       # For compiling directory paths

import logging
logger = logging.getLogger('log')     # Set the logger



class Log_frame(tk.Frame):
    '''The plotting and logging frame'''
    def __init__(self, parent, ports):
        tk.Frame.__init__(self, parent, width=2000, height=900)
        self.parent = parent
        self.ports = ports
        self.Widgets()


    def Widgets(self):
        '''Shapes the frame's widgets'''
        # Check if device exists
        if self.ports.itc != None:
            self.plot1 = Temperature_plot(self, self.ports)
            self.plot1.pack(side='top', fill='both', expand=True)

        if self.ports.ips != None:
            self.plot2 = Field_plot(self, self.ports)
            self.plot2.pack(side='top', fill='both', expand=True)



class Log_plot(tk.Frame):
    '''The base for single plot frame'''
    def __init__(self, parent, ports):
        tk.Frame.__init__(self, parent, padx=5, pady=5)
        self.parent = parent
        self.ports = ports

        # Initiate daughter parameters
        self.Set_params()

        # Set parameters
        self.y_len = len(self.y_list)

        # Create directory if not existent
        try: os.mkdir('log_files')
        except: pass
        try: os.mkdir(self.file_directory)
        except: pass

        # Build widgets
        self.Widgets()

    
    def Widgets(self):
        '''Places the widgets and plot'''
        # Label
        self.label_title = tk.Label(self, text=self.title)
        self.label_title.config(font=('Courier', 16))
        self.label_title.pack(side='top')

        # Control buttons frame
        self.frame_buttons = tk.Frame(self)
        self.frame_buttons.pack(side='top', fill='x')
        self.Buttons()

        self.Plot_setup()


    def Plot_setup(self):
        ''' Creates the plot and main settings'''
        # Generate plot
        self.fig = Figure(figsize=(5,3), dpi=100)
        self.axes = self.fig.add_subplot(111)
        #self.fig.subplots_adjust(bottom=0.16, left=0.10, right=0.96, top=0.94)

        # Generate canvas and toolbar
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=True)
        self.canvas._tkcanvas.pack(side='top', fill='both', expand=True)

        # Settings
        self.axes.grid()
        self.axes.set_xlabel('Time')
        self.axes.set_ylabel(self.y_axis)

        # Prepare data lists
        log = self.Update()
        self.x = [datetime.datetime.now()]
        self.y = [[float(y[:-1])] for y in log[1:1+self.y_len]]

        self.lines = list()

        # Formats x axis in date format
        # Skip for auto settings
        #date_format = matplotlib.dates.DateFormatter('%H:%M:%S')
        #self.axes.xaxis.set_major_formatter(date_format)
        self.fig.autofmt_xdate(rotation=30) # Rotated lables

        # Add traces
        for i,trace in enumerate(self.y):
            line, = self.axes.plot(self.x, trace, 'o-', label=self.y_list[i])
            self.lines.append(line)

        # Add twin plot if enabled
        if self.twin:
            self.y2_len = len(self.y2_list)
            self.y2 = [[float(y[:-1])] for y in
                log[1+self.y_len : 1+self.y_len+self.y2_len]]

            # Add second axes, sharing x axis
            self.axes2 = self.axes.twinx() 
            self.axes2.set_ylabel(self.y_axis)
            for i,trace in enumerate(self.y2):
                line, = self.axes2.plot(self.x, trace, 's-', color='tab:green',
                    label=self.y2_list[i])
                self.lines.append(line)

        # Add legends
        self.axes.legend(self.lines, [line.get_label() for line in self.lines])


    def Clear_plot(self, event=None):
        '''Clears all but the last point in the plot and replots'''
        self.x = [self.x[-1]]
        for i in range(self.y_len):
            self.y[i] = [self.y[i][-1]]
            self.lines[i].set_ydata(self.y[i])
            self.lines[i].set_xdata(self.x)
        self.axes.relim()
        self.axes.autoscale() # Enables autoscale for axes
        # Clear the twin
        if self.twin:
            for i in range(self.y2_len):
                self.y2[i] = [self.y2[i][-1]]
                self.lines[i+self.y_len].set_ydata(self.y2[i])
                self.lines[i+self.y_len].set_xdata(self.x)
            self.axes2.relim()
            self.axes2.autoscale()

        self.canvas.draw() # Redraw canvas


    def Buttons(self):
        '''The logging control buttons'''
        # Buttons
        self.button_log = ttk.Button(self.frame_buttons, text='Start log',
            command=self.Start_log)
        self.button_log.pack(side='left')

        # Select frequency
        ttk.Label(self.frame_buttons, text='  Interval: ').pack(side='left')
        self.dict_times = {'5s':5000, '20s':20000, '1m':60000,
            '5m':5*60*1000, '20m':20*60*1000, '1h':60*60*1000}
        self.var_time = tk.StringVar(self)
        self.var_time.set('20s') # Default interval
        self.time = self.dict_times[self.var_time.get()]
        self.combo_time = ttk.Combobox(self.frame_buttons, width=7,
            state='readonly', values=list(self.dict_times.keys()),
            textvar=self.var_time)
        self.combo_time.pack(side='left')
        self.combo_time.bind("<<ComboboxSelected>>", self.Change_time)

        # Button Clear plot
        self.button_clear = ttk.Button(self.frame_buttons, text='Clear plot',
            command=self.Clear_plot)
        self.button_clear.pack(side='right')

        # Button Import log
        self.button_import = ttk.Button(self.frame_buttons, text='Import log',
            command=self.Set_import)
        self.button_import.pack(side='right')

        # Button Autoscale
        self.button_autoscale = ttk.Button(self.frame_buttons,
            text='Autoscale', command=self.Autoscale)
        self.button_autoscale.pack(side='right')

        # Button Fix scale
        if self.twin:
            self.button_fixscale = ttk.Button(self.frame_buttons,
                text='Fixed y', command=self.Fixscale)
            self.button_fixscale.pack(side='right')


    def Start_log(self, event=None):
        '''Starts the logging'''
        self.button_log['text'] = 'Stop log'
        self.button_log['command'] = self.Stop_log
        self.logging = self.button_log.after(10, self.Log)


    def Stop_log(self, event=None):
        '''Interrupts the logging'''
        self.button_log['text'] = 'Start log'
        self.button_log['command'] = self.Start_log
        self.button_log.after_cancel(self.logging)
        self.logging = None # Removes reference to logging event


    def Change_time(self, event=None):
        '''Change of logging interval, as option is selected from box'''
        logger.info('Logging interval changed to: '+self.var_time.get())
        self.time = self.dict_times[self.var_time.get()]
        # Logs now and continues with new interval
        if self.button_log['text'] == 'Stop log':
            self.button_log.after_cancel(self.logging)
            self.logging = self.button_log.after(10, self.Log)


    def Autoscale(self, event=None):
        '''Button function to reenable autoscaling'''
        self.axes.autoscale()
        if self.twin:
            self.axes2.autoscale()
        self.canvas.draw()


    def Fixscale(self, event=None):
        '''Button that fixes right scale to left'''
        logger.debug('Setting both y axes to same')
        # Not working yet
        """
        # Find max and min
        y_min = min(self.axes.get_ylim()[0], self.axes2.get_ylim()[0])
        y_max = max(self.axes.get_ylim()[1], self.axes2.get_ylim()[1])
        diff = y_min-y_max
        # Apply to both
        self.axes.set_ylim((y_min, y_max))
        self.axes2.set_ylim((y_min, y_max))
        # Fix margins
        #self.axes.autoscale_view() 
        #self.axes2.autoscale_view() 
        self.axes.relim()
        self.axes2.relim()
        """
        # Doesnt work well if twins are too far apart
        self.axes2.set_ylim(self.axes.get_ylim())
        # Redraw canvas
        self.canvas.draw()


    
    def Set_import(self, event=None):
        '''Button to set time and import data to log plot'''
        # Try to get date input
        try:
            date = tk.simpledialog.askstring('Start date',
                'Insert starting date, eg. 24.09.2020')
            date = datetime.datetime.strptime(date, '%d.%m.%Y')
        except: 
            messagebox.showerror('Bad date format',
                'Please insert date in same format as example')
            return

        # Try to get time input
        try:
            time = tk.simpledialog.askstring('Start time',
                'Insert starting time, eg. 13:49:00')
            time = datetime.datetime.strptime(time, '%H:%M:%S')
        except:
            messagebox.showerror('Bad time format',
                'Please insert time in same format as example')
            return

        # Call import log function by combining inserted date and time
        self.Import_log(datetime.datetime.combine(date.date(), time.time()))


    def Log(self):
        '''Actions to do for every log, and call next repetition'''
        log = self.Update()

        # Add to log file
        self.Write_log(log)

        # Add to plot lists
        if not None in log: # Check if all values were read
            self.x.append(log[0])
            for i in range(self.y_len):
                self.y[i].append(float(log[i+1][:-1])) # remove K at end
                self.lines[i].set_ydata(self.y[i])
                self.lines[i].set_xdata(self.x)
            self.axes.relim()
            self.axes.autoscale_view() 
            if self.twin:
                for i in range(self.y2_len):
                    self.y2[i].append(float(log[i+1+self.y_len][:-1]))
                    self.lines[i+self.y_len].set_ydata(self.y2[i])
                    self.lines[i+self.y_len].set_xdata(self.x)
                self.axes2.relim()
                self.axes2.autoscale_view()
            self.canvas.draw() # Redraw canvas

        # Continue logging
        self.logging = self.button_log.after(self.time, self.Log)


    def Write_log(self, log):
        '''Writes the log data into a log file'''
        file_name = log[0].strftime('%Y%m%d') + self.file_end
        file_path = os.path.join(self.file_directory, file_name)

        with open(file_path, 'a', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            # Add line
            line = []
            line.append(log[0].strftime('%H:%M:%S'))
            for i in log[1:]:
                if i == None:
                    line.append('')
                else:
                    try: # Keep if float
                        line.append(float(i))
                    except: # Try to strip unit
                        line.append(float(i[:-1]))
            writer.writerow(line)


    def Import_log(self, start_time):
        '''Imports the data from log files, to add to plots
            start_time in datetime.datetime format'''
        # Set up lists, dont use self as this is just internal to this import
        file_list = list()
        date_list = list()

        for entry in os.scandir(self.file_directory):
            if entry.is_file():
                file_list.append(os.path.join(self.file_directory,
                    entry.name))
                date = entry.name.split('_')[0] # Get date string
                date = datetime.datetime.strptime(date, '%Y%m%d').date()
                date_list.append(date)

        # Clear plot lists
        self.x = []
        self.y = [[] for i in range(self.y_len)]
        if self.twin:
            self.y2 = [[] for i in range(self.y2_len)]

        # Open files and extract data
        for i,file in enumerate(file_list):
            # Find files with late enough dates
            if start_time.date() <= date_list[i]:
                with open(file, "r", newline='') as f:
                    reader= csv.reader(f, delimiter=';')
                    for row in reader:
                        # Import into datetime format
                        time = datetime.datetime.strptime(row[0], '%H:%M:%S')
                        time = datetime.datetime.combine(
                            date_list[i], time.time())
                        # Write values if time matches
                        if time >= start_time:
                            if '' not in row:
                                self.x.append(time)
                                for j in range(self.y_len):
                                    self.y[j].append(float(row[j+1]))
                                if self.twin:
                                    for j in range(self.y2_len):
                                        self.y2[j].append(
                                            float(row[j+1+self.y_len]))
        
        # Replot
        for i in range(self.y_len):
            self.lines[i].set_ydata(self.y[i])
            self.lines[i].set_xdata(self.x)
        self.axes.relim()
        self.axes.autoscale()
        if self.twin:
            for i in range(self.y2_len):
                self.lines[i+self.y_len].set_ydata(self.y2[i])
                self.lines[i+self.y_len].set_xdata(self.x)
            self.axes2.relim()
            self.axes2.autoscale()
        self.canvas.draw()


    def Update(self):
        '''Has to be defined in daughter, depending on the type of log'''
        return []

    
    def Set_params(self):
        '''Params should be evalued in the daughter class'''
        self.device = None
        self.title = None
        self.y_axis = None
        self.y_list = list()
        self.file_end = None
        self.file_directory = None
        self.twin = None
        self.y2_list = list()



class Field_plot(Log_plot):
    '''Inherits the Log plot framwork and holds Field plot specifics'''
    def __init__(self, parent, ports):
        '''Initializes the log plot'''
        Log_plot.__init__(self, parent, ports)


    def Update(self):
        '''Requests data from ips and adds to plot'''
        sensor = self.parent.parent.ips_frame.frame_select.var_sens.get()
        flog = self.ports.Get_Flog(sensor)
        logger.debug(flog)
        return flog

    
    def Set_params(self):
        '''Sets the params for the field plot'''
        self.device = 'ips'
        self.title = 'Field log'
        self.y_axis = 'Field (T)'
        self.y_list = ['Set F', 'Current F', 'Peristent F']
        self.file_end = '_Field.log'
        self.file_directory = os.path.join('log_files','field')

        self.twin = False



class Temperature_plot(Log_plot):
    '''Inherits the Log plot framwork and holds Field plot specifics'''
    def __init__(self, parent, ports):
        '''Initializes the log plot'''
        Log_plot.__init__(self, parent, ports)
        
    
    def Update(self):
        '''Requests data from itc and adds to plot'''
        sensor = self.parent.parent.itc_frame.var_sens.get()
        tlog = self.ports.Get_Tlog(sensor)
        logger.debug(tlog)
        return tlog


    def Set_params(self):
        '''Sets the params for the temperature plot'''
        self.device = 'itc'
        self.title = 'Temperature log'
        self.y_axis = 'Temperature (K)'
        self.y_list = ['Set T', 'Current T']
        self.file_end = '_Temp.log'
        self.file_directory = os.path.join('log_files','temperature')

        # Add second axis plot
        self.twin = True
        self.y2_list = ['Probe T']


