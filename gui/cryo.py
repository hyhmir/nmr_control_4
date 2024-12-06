'''Code to add a window with the cryogen log plot''' 

# Imports
import tkinter as tk    # Gui package

# Plotting
import matplotlib
matplotlib.use('TkAgg') # Selects tkinter backend
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
    NavigationToolbar2Tk)
from matplotlib.figure import Figure
# Logging
import datetime # A format for dates and time
import csv # For importing and exporting CSV files
import os # For compiling directory paths
# Data manipulation and fitting (Necessary??)
#import numpy as np
#from scipy.optimize import curve_fit



class Cryo_application(tk.Frame):
    '''Builds the window for plot of the log'''
    def __init__(self, parent):
        '''Initialize the toplevel frame'''

        self.parent = parent
        #self.parent.wm_title('Cryogen log plot')
        #self.parent.minsize(height=768, width=1024)

        # Creates the popup window as self
        tk.Frame.__init__(self, parent)
        self.pack(fill='both', expand=True)

        self.Add_plot()


    def Add_plot(self):
        '''Packs and positions all the frames'''
         # Plot canvas
        self.fig = Figure(figsize=(5,3), dpi=100)
        self.axes = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=True)
        self.canvas._tkcanvas.pack(side='top', fill='both', expand=True)

        # Settings
        self.axes.grid()
        self.axes.set_xlabel('Time')
        self.axes.set_ylabel('Cryogen sensor levels (%)')

        # Format the date display
        #date_format = matplotlib.dates.DateFormatter('%H:%M:%S')
        #self.axes.xaxis.set_major_formatter(date_format)
        self.fig.autofmt_xdate(rotation=30)

        # Get the data
        self.Import_data()

        # Add traces
        self.line_he, = self.axes.plot(self.x_he, self.y_he, 'o-', label='He level')
        self.line_n2, = self.axes.plot(self.x_n2, self.y_n2, 'o-', label='N2 level')

        # Set default x limits.
        _last_point = max(self.x_he[-1], self.x_n2[-1])
        self.axes.set_xlim(_last_point - datetime.timedelta(days=10), _last_point + datetime.timedelta(days=1)) # this upper limit is temporary. TODO make this change in updating of the cryo plot.

        # Add legends
        self.axes.legend()


    def Import_data(self):
        '''Imports data and returns data lists'''
        # Set file directories
        self.file_directory = os.path.join('log_files','sensors')
        self.file_list = list()
        self.date_list = list()

        # Find all files and remember dates
        for entry in os.scandir(self.file_directory):
            if entry.is_file():
                self.file_list.append(os.path.join(self.file_directory,
                    entry.name))
                self.date_list.append(entry.name.split('_')[0])

        # Set up the lists for data
        self.x_he = list()
        self.y_he = list()
        self.x_n2 = list()
        self.y_n2 = list()

        # Open all files and extract data
        for i,file in enumerate(self.file_list):
            with open(file, "r", newline='') as f:
                reader = csv.reader(f, delimiter=';')
                for row in reader:
                    # Import into datetime format
                    d = datetime.datetime.strptime(
                        self.date_list[i]+row[0], '%Y%m%d%H:%M:%S')
                    # Append the non empty entries, removing %
                    try:
                        self.y_he.append(float(row[1]))
                        self.x_he.append(d)
                    except: pass
                    try:
                        self.y_n2.append(float(row[2]))
                        self.x_n2.append(d)
                    except: pass

        # List absolute times in hours
        self.xx_he = [(xx-self.x_he[0]).total_seconds()/3600
            for xx in self.x_he]
        self.xx_n2 = [(xx-self.x_n2[0]).total_seconds()/3600
            for xx in self.x_n2]

    def Update(self, timestamp, he_level, n2_level):
        """
        Updates the cryo plot with one datapoint.
        TODO: 
         - Allow adding only N2 or He point, without the other.
         - Possibly allow adding an array of data.
        """
        self.x_he.append(timestamp)
        self.y_he.append(he_level)
        self.x_n2.append(timestamp)
        self.y_n2.append(n2_level)
        self.line_he.set_xdata(self.x_he)
        self.line_he.set_ydata(self.y_he)
        self.line_n2.set_xdata(self.x_n2)
        self.line_n2.set_ydata(self.y_n2)

        self.canvas.draw() # Redraw canvas


if __name__ == '__main__' and 0:
    # Run in VSC as 
    # C:\Python\projects\Mercury_control> pipenv run .\gui\cryo.py
    # For testing just the cryo view.
    # even with __name__ == '__main__', this still runs from main. Don't know why.
    cryo_window = tk.Tk("test")
    Cryo_application(cryo_window)
    cryo_window.mainloop()