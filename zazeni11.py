##############################################################################
#  zazeni in uzivaj ob raziskovanju skrivnosti vesolja                       #
##############################################################################

# uvozimo vse potrebne module
import subprocess
from tmag11 import Tecmag
from gui11_iii import NMR_GUI
import threading
import time
import ctypes
stop_thread = False

def find_window(window_title):
    """Search for a window by its title."""
    hwnd = ctypes.windll.user32.FindWindowW(None, window_title)
    return hwnd != 0 # Return True if the window is found

def find_widow():
    global stop_thread
    while True:
        if stop_thread:
            print("Background task is stopping...")
            break
        if find_window("TNMR"): # Adjust title as needed
            print("CDyalog warning window detected!")
            # Optional: Take action (close, log, etc.)
        else:
            print("No warning window detected.")
        
        time.sleep(1) # Check every second

# zazenemo aplikacijo
if __name__ == "__main__":
    tecmag = Tecmag()
    tecmag.Parameter_setup()
    
    thread = threading.Thread(target=find_widow)
    thread.start()
    gui = NMR_GUI(tecmag, tecmag)
    gui.mainloop()
    stop_thread = True
    tecmag.app.Abort
    tecmag.app.CloseActiveFile
    tecmag.app.CloseActiveFile
    subprocess.call("TASKKILL /F /IM TNMR.exe", shell=True)
