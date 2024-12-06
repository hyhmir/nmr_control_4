import gui
import tkinter as tk
import logging
logger = logging.getLogger('log')     # Set the logger

if __name__ == "__main__":
    '''Executes when this is the main aplication'''
    logger.info('Starting main application TNMR_control')


    # Initiate gui interface
    root = tk.Tk()
    gui.main.TNMR_application(root)
    root.mainloop()

