import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk


def Main_frame(self, frame):
    '''Configures main frame of GUI - Current data and fourier transform plots'''
# Experiment buttons, NSC indicator
    self.nuttons = tk.Frame(frame)
    self.nuttons.grid(row=0, column=0, sticky='w')

    self.acs = tk.Label(self.nuttons, text=self.nsc)
    start_button = tk.Button(self.nuttons, text="Start Experiment", command=self.start_experiment)
    stop_button = tk.Button(self.nuttons, text="Stop Experiment", command=self.stop_experiment)
    abort_button = tk.Button(self.nuttons, text="Abort Experiment", command=self.abort_experiment)

    self.check_real_var = tk.IntVar()
    self.check_real = tk.Checkbutton(self.nuttons, text="real", variable=self.check_real_var, command=self.UpdateFourier, onvalue=True, offvalue=False)
    self.check_real.select()

    self.check_imag_var = tk.IntVar()
    self.check_imag = tk.Checkbutton(self.nuttons, text="imag", variable=self.check_imag_var, command=self.UpdateFourier, onvalue=True, offvalue=False)
    self.check_imag.select()

    self.check_magn_var = tk.IntVar()
    self.check_magn = tk.Checkbutton(self.nuttons, text="magn", variable=self.check_magn_var, command=self.UpdateFourier, onvalue=True, offvalue=False)
    self.check_magn.select()

    start_button.pack(side='left', fill='both')
    stop_button.pack(side='left', fill='both')
    abort_button.pack(side='left', fill='both')
    self.acs.pack(side='left', fill='both')
    self.check_real.pack(side="left", fill="both")
    self.check_imag.pack(side="left", fill="both")
    self.check_magn.pack(side="left", fill="both")


# Data plot, toolbar, x of data vertical
    self.figure1 = Figure(figsize=(10, 6), dpi=100)
    self.canvas1 = FigureCanvasTkAgg(self.figure1, master=frame)
    self.canvas1.mpl_connect("button_press_event", self.on_click1)
    self.canvas1.draw()
    self.canvas1.get_tk_widget().grid(column=0, row=1, sticky='ns')

    self.ax1 = self.figure1.add_subplot()
    # self.ax1.set_ylim([-100, 100])
    self.ax1.set_xlabel('time [ms]')
    self.ax1.grid()
    self.figure1.canvas.draw()
    self.figure1.canvas.flush_events()

# Fourier plot, toolbar, x of fourier vertical
    self.figure2 = Figure(figsize=(10, 6), dpi=100)
    self.canvas2 = FigureCanvasTkAgg(self.figure2, master=frame)
    self.canvas2.mpl_connect("button_press_event", self.on_click2)
    self.canvas2.draw()
    self.canvas2.get_tk_widget().grid(column=1, row=1, sticky='ns')

    self.ax2 = self.figure2.add_subplot()
    # self.ax2.set_ylim([-20000, 20000])
    self.ax2.set_xlabel('freq [MHz]')
    # self.ax2.invert_xaxis()
    self.ax2.grid()
    self.figure2.canvas.draw()
    self.figure2.canvas.flush_events()

# Data plot toolbar
    self.tulbar1 = tk.Frame(frame)
    self.tulbar1.grid(row=2, column=0)

    self.xclickdata1 = tk.Label(self.tulbar1, text=self.varclickxdata)
    self.xclickdata2 = tk.Label(self.tulbar1, text=self.varclickxdata)
    self.xclickindex11 = tk.Label(self.tulbar1, text=self.varclickxdata)
    self.xclickindex12 = tk.Label(self.tulbar1, text=self.varclickxdata)
    self.autodat = tk.Button(self.tulbar1, text='autoscale', command=self.Autoscaledat)

    self.toolbar1 = NavigationToolbar2Tk(self.canvas1, self.tulbar1, pack_toolbar=False)
    self.toolbar1.update()

    self.xclickdata1.pack(side='left', fill='both')
    self.xclickdata2.pack(side='left', fill='both')
    self.xclickindex11.pack(side='left', fill='both')
    self.xclickindex12.pack(side='left', fill='both')
    self.toolbar1.pack(side='left', fill='both')
    self.autodat.pack(side='left', fill='both')

# Fourier plot toolbar
    self.tulbar2 = tk.Frame(frame)
    self.tulbar2.grid(row=2, column=1)

    self.xclickfour1 = tk.Label(self.tulbar2, text=self.varclickxfour)
    self.xclickfour2 = tk.Label(self.tulbar2, text=self.varclickxfour)
    self.xclickindex21 = tk.Label(self.tulbar2, text=self.varclickxdata)
    self.xclickindex22 = tk.Label(self.tulbar2, text=self.varclickxdata)
    self.autofur = tk.Button(self.tulbar2, text='autoscale', command=self.Autoscalefur)

    self.toolbar2 = NavigationToolbar2Tk(self.canvas2, self.tulbar2, pack_toolbar=False)
    self.toolbar2.update()

    self.xclickfour1.pack(side='left', fill='both')
    self.xclickfour2.pack(side='left', fill='both')
    self.xclickindex21.pack(side='left', fill='both')
    self.xclickindex22.pack(side='left', fill='both')
    self.toolbar2.pack(side='left', fill='both')
    self.autofur.pack(side='left', fill='both')

def Automatisation_frame(self, frame):
    '''Configures frame for automatisation experiment - integral of data with respect to changing parameter'''

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    self.figure3 = Figure(figsize=(10, 6), dpi=100)
    self.canvas3 = FigureCanvasTkAgg(self.figure3, master=frame)
    self.canvas3.draw()
    self.canvas3.get_tk_widget().grid(row=0, column=0, sticky='nsew')

    self.ax3 = self.figure3.add_subplot()
    self.ax3.set_ylim([-100, 100])
    self.ax3.set_xlabel('expparams')
    self.ax3.grid()
    self.figure3.canvas.draw()
    self.figure3.canvas.flush_events()

    self.tulbar3 = tk.Frame(frame)
    self.tulbar3.grid(row=1, column=0)

    self.toolbar3 = NavigationToolbar2Tk(self.canvas3, self.tulbar3, pack_toolbar=False)
    self.toolbar3.update()
    self.toolbar3.pack(side='left', fill='both')


def Sweep_frame(self, frame):
    '''Configures frame for sweep experiment - integral of data with respect to linearly changing observe frequency'''

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    self.figure4 = Figure(figsize=(10, 6), dpi=100)
    self.canvas4 = FigureCanvasTkAgg(self.figure4, master=self.sweepframe)
    self.canvas4.draw()
    self.canvas4.get_tk_widget().grid(row=0, column=0, sticky='nsew')

    self.ax4 = self.figure4.add_subplot()
    self.ax4.set_ylim([-100, 100])
    self.ax4.set_xlabel('expparams')
    self.ax4.grid()
    self.figure4.canvas.draw()
    self.figure4.canvas.flush_events()

    self.tulbar4 = tk.Frame(self.sweepframe)
    self.tulbar4.grid(row=1, column=0)

    self.toolbar4 = NavigationToolbar2Tk(self.canvas4, self.tulbar4, pack_toolbar=False)
    self.toolbar4.pack(side='left', fill='both')
    self.toolbar4.update()


def T1_frame(self, frame):
    '''Configures frame for T1 experiment - integral of data with respect to exponentialy changing d5 delay'''

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    self.figure5 = Figure(figsize=(10, 6), dpi=100)
    self.canvas5 = FigureCanvasTkAgg(self.figure5, master=self.T1frame)
    self.canvas5.draw()
    self.canvas5.get_tk_widget().grid(row=0, column=0, sticky='nsew')

    self.ax5 = self.figure5.add_subplot()
    self.ax5.set_ylim([-100, 100])
    self.ax5.set_xlabel('expparams')
    self.ax5.grid()
    self.ax5.set_xscale('log')
    self.figure5.canvas.draw()
    self.figure5.canvas.flush_events()

    self.tulbar5 = tk.Frame(self.T1frame)
    self.tulbar5.grid(row=1, column=0)

    self.toolbar5 = NavigationToolbar2Tk(self.canvas5, self.tulbar5, pack_toolbar=False)
    self.toolbar5.pack(side='left', fill='both')
    self.toolbar5.update()

def T2_frame(self, frame):
    '''Configures frame for T2 experiment - integral of data with respect to linearly changing tau delay'''

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    self.figure6 = Figure(figsize=(10, 6), dpi=100)
    self.canvas6 = FigureCanvasTkAgg(self.figure6, master=frame)
    self.canvas6.draw()
    self.canvas6.get_tk_widget().grid(row=0, column=0, sticky='nsew')

    self.ax6 = self.figure6.add_subplot()
    self.ax6.set_ylim([-100, 100])
    self.ax6.set_xlabel('expparams')
    # self.ax6.set_yscale("log")
    self.ax6.grid()
    self.figure6.canvas.draw()
    self.figure6.canvas.flush_events()

    self.tulbar6 = tk.Frame(frame)
    self.tulbar6.grid(row=1, column=0)

    self.toolbar6 = NavigationToolbar2Tk(self.canvas6, self.tulbar6, pack_toolbar=False)
    self.toolbar6.pack(side='left', fill='both')
    self.toolbar6.update()
