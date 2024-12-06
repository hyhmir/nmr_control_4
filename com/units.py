'''Package for handling the SCPI unit logic'''
'''Assuming all units are 1 letter long...'''
'''Turns out that its not how the communications work!!!'''

# Import
from tkinter import messagebox


class Units():
    '''Class that reads values with unit and converts'''
    # Define internal dictionaries
    # Dictionary of possible units; unit : default prefix
    units = {
        'K' : '',
        'A' : '',
        'V' : '',
        'W' : ''
    }
    # Dictionary of prefixes; prefix : value
    prefixes = {
        'n' : 0.000000001,
        'u' : 0.000001,
        'm' : 0.001,
        '' : 1.0,
        'k' : 1000.0,
        'M' : 1000000.0,
        'G' : 1000000000.0
    }


    def __init__(self, value, unit):
        '''Initializes class, takes two strings, reads prefix'''
        self.value = float(value)
        self.unit = unit[-1]
        self.prefix = unit[:-1]
        # Unitless form
        self.unitless = self.value * self.prefixes[self.prefix]
        # Default form
        self.default = self.unitless * self.prefixes[self.units[self.unit]]


    def Return(self, prefix=None, warn=True):
        '''Returns the value of given number, defaulting no prefix'''
        if prefix == None:
            return self.default
        elif prefix in self.prefixes:
            return self.unitless * self.prefixes[prefix]
        elif warn:
            messagebox.showerror('Unit prefix error',
                'The given prefix "'+str(prefix)+'" is not recognised')
        return None

    

    # Editing behaviour of object
    def __str__(self):
        '''Gives the object in string form, SCPI style if using str(Object)'''
        return str(self.value) + ':' + self.prefix + self.unit
    

    def __repr__(self):
        '''Return mode of object when using; return (Object)'''
        self.Return(prefix=None, warn=False)



if __name__ == "__main__":
    '''Runs if this is the excecuted file'''
    A = Units('12.345','mV')
    print(A.Return())
    print(A)

