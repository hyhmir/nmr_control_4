'''Daughter boards on Mercury devices'''

# Imports
from tkinter import messagebox
#from units import Units


# Global variables



# Daughter board classes
class Device():
    '''The general daughter board/device class'''
    # List the regular set options; option : command
    set_options = dict()    # These take a setting value
    # List the regular read options; option : command
    read_options = dict()

    def __init__(self, parent, string):
        '''Takes the 3 part string to create the daughter class'''
        self.parent = parent # Reference to parent board
        self.string = string
        split = string.split(':')
        self.type = split[2]
        self.name = split[1]
        # Finds appropriate commands for given device
        self.Load_options()


    def Read_direct(self, command, warn=True):
        '''Asks parent to read given command'''
        s = self.string + ':' + command
        return self.parent.Read_direct(s, warn=warn)


    def Set_direct(self, command, query=True, warn=True):
        '''Asks parent to set given command'''
        s = self.string + ':' + command
        return self.parent.Set_direct(s, query=query, warn=warn)


    def Read_option(self, option, warn=True):
        '''Default reading function with validity check'''
        # Prepares command string and calls
        s = 'READ:'+ self.string +':'+ self.read_options[option]
        x = self.parent.Exchange(s, warn=warn)

        # Check for deeper errors
        if x == None:
            return None

        split = x.split(':')
        # VALID does not occur on ITC. Take last part of string
        return split[-1]

    
    def Set_option(self, option, value, query=True, warn=True):
        '''Default setting function with validity check'''
        
        # Prepares command string and calls
        s = 'SET:'+ self.string +':'+ self.set_options[option] +':'+ str(value)

        # Pops up confirmation window
        if query:
            if not messagebox.askyesno('Mercury',
                    'Would you like to "'+ s +'" ?'):
                return None

        x = self.parent.Exchange(s, warn=warn)

        # Check for deeper errors
        if x == None:
            return None

        # Check for validity
        split = x.split(':')
        if split[-1] == 'VALID':
            return True
        elif warn:
            messagebox.showerror('Set error',
                'Something went wrong when setting value')
        return None


    def Load_options(self):
        '''Loads list of commands for given device type'''
        # Think about implementing in external file...
        # Exclude dangerous settings for now

        # iTC devices
        if self.type == 'AUX':
            readwrite = {
                'GMIN' : 'GMIN'         # Set minimum flow
            }
            read = {
                'PERC' : 'SIG:PERC',    # Valve open percentage
                'STEP' : 'SIG:STEP',    # Valve position
            }
        elif self.type == 'HTR':
            readwrite = {
                'VLIM' : 'VLIM',        # Heater voltage limit
                'PMAX' : 'PMAX',        # Heater power limit
                'V' : 'SIG:VOLT'        # Heater voltage
            }
            read = {
                'CURR' : 'SIG:CURR',    # Heater current
                'POWR' : 'SIG:POWR'     # Heater power dissipation
            }
        elif self.type == 'TEMP':
            readwrite = {
                'HOTL' : 'CAL:HOTL',    # High temperature limit
                'COLDL' : 'CAL:COLDL',  # Low temperature limit
                'TSET' : 'LOOP:TSET',   # Set temerature
                'P' : 'LOOP:P',         # Proportional gain
                'I' : 'LOOP:I',         # Integral gain
                'D' : 'LOOP:D',         # Differential gain
                'HSET' : 'LOOP:HSET',   # Heater percentage
                'FLSET' : 'LOOP:FSET',  # Flow percentage
                'RSET' : 'LOOP:RSET',   # Ramp rate
                'HTR' : 'LOOP:HTR',     # Asign heater to temperature loop
                'AUX' : 'LOOP:AUX',     # Asign aux device to temperature loop
                'RENA' : 'LOOP:RENA',   # Enable/disable ramp mode
                'FAUT' : 'LOOP:FAUT',   # Enable/disable flow control
                'ENAB' : 'LOOP:ENAB'    # Enable/disable heater PID control
            }
            read = {
                'TEMP' : 'SIG:TEMP',     # Check current temperature
            }
        # iPS devices
        elif self.type == 'PSU':
            readwrite = {
                'CSET' : 'SIG:CSET',    # Target current
                'FSET' : 'SIG:FSET',    # Target field
                'RCST' : 'SIG:RCST',    # Target ramp rate A/min
                'RFST' : 'SIG:RFST',    # Target ramp rate T/min
                'SWHT' : 'SIG:SWHT',    # Switch heater status (with check)
                'ACTN' : 'ACTN'        # Ramp status
            }
            read = {
                'VOLT' : 'SIG:VOLT',    # Magnet output voltage
                'CURR' : 'SIG:CURR',    # Magnet output current
                'PCUR' : 'SIG:PCUR',    # Magnet output persistent current
                'FLD' : 'SIG:FLD',      # Field in T
                'PFLD' : 'SIG:PFLD',    # Persistent field in T
                'RCUR' : 'SIG:RCUR',    # Actual current rate in A/min
                'RFLD' : 'SIG:RFLD',    # Field rate in T/min
            }
        elif self.type == 'LVL':
            readwrite = {
                
            }
            read = {
                'HLEV' : 'SIG:HEL:LEV', # Helium level
                'HRES' : 'SIG:HEL:RES', # Helium sensor resistance
                'FREQ' : 'SIG:NIT:FREQ',# Nitrogen sensor frequency
                'NLEV' : 'SIG:NIT:LEV', # Nitrogen sensor level
            }
        # Missing
        else:
            messagebox.showerror('Device error',
                'The given device is not listed:'+ self.type)
            return
        
        self.set_options.update(readwrite)
        self.read_options.update(read)
        self.read_options.update(readwrite)



if __name__ == "__main__":
    '''Runs if this is the excecuted file'''
    pass
        

