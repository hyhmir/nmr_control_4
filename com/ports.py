'''Finding and identifying comports'''

# Imports

import serial
import serial.tools.list_ports
from tkinter import messagebox
from com.devices import Device
from datetime import datetime

# Get strip function
from gui.funct import Strip_T

import logging
logger = logging.getLogger('log')     # Set the logger

# Global variables
READ_LEN = 200
ENC = 'utf-8'
APP_NAME = 'Mercury'
PORT_TIMEOUT = 0.3



class Comport():
    '''Class for talking to comports'''
    def __init__(self, port):
        '''Initializes comport'''
        self.name = port
        self.ser = serial.Serial(port, timeout=PORT_TIMEOUT) # Fails if short
        self.ser.close()


    def __enter__(self):
        '''Opening of comport'''
        if self.ser.is_open:
            logger.warning(self.name+': Why am i open?')
        if not self.ser.is_open:
            self.ser.open()
        return self


    def __exit__(self, E_type, E_value, E_traceback):
        '''Closing of comport'''
        self.ser.close()
        logger.info('Closing: "'+self.name+'", Errors:',
            (E_type,E_value,E_traceback))
        return (E_type,E_value,E_traceback)


    def Identify(self):
        '''Sends the '*IDN?' command to comport and checks response'''
        self.ser.open()
        self.ser.write('*IDN?\n'.encode(ENC))
        x = self.ser.read(READ_LEN).decode(ENC)
        self.ser.close()
        logger.info(self.name + ': ' + x.rstrip())
        return x


    def Exchange(self, string, str_len=READ_LEN, warn=True):
        '''Talks to comport device uscing SCPI, prints, returns string'''
        #logger.info('>>>' + string)
        print('>>>' + string)
        self.ser.open()
        self.ser.write((string + '\n').encode(ENC))
        x = self.ser.read(str_len)
        self.ser.close()
        x = x.decode(ENC).rstrip()
        #logger.info('<<<' + x)
        print('<<<' + x)

        # Check for errors:
        split = x.split(':')
        msg = ''
        if x == '':
            msg = 'Did not recieve any repsonse: '+string
        elif 'INVALID' in split:
            msg = 'The command cannot be interpreted: '+string
        elif 'NOT_FOUND' in split:
            msg = 'The adressed device could not be found: '+string
        elif 'N/A' in split:
            msg = 'The function does not apply to the adressed device: '+string
        elif 'DENIED' in split:
            msg = 'No permission to change the adressed parameter: '+string

        if msg:
            logger.error(msg)
            if warn:
                messagebox.showerror('COMport error', msg)
            return None

        return x



# Subclass of Comport
class Mercury(Comport):
    '''Talks to Mercury devices'''

    def Find_daughters(self, test=False):
        '''Queries for list of daughter boards'''
        if test:
            s = 'STAT:DEV:MB0.T1:TEMP:DEV:MB1.H1:HTR:DEV:DB0.A1:AUX'
        else:
            s = self.Read_direct('SYS:CAT')
        if s is not None:
            s = s.split(':DEV:')[1:]
        self.daughters = s

    
    def Build_daughters(self, test=False):
        '''Initiates the daughter boards'''
        try:
            daughters = self.daughters
        except KeyError():
            self.Find_daughters(test = test)
            daughters = self.daughters

        for d in daughters:
            name = d.split(':')[0]
            self.__dict__[name] = Device(self, 'DEV:'+ d)


    def Read_direct(self, command, warn=True):
        '''Sends read command to main board and returns response string'''
        s = 'READ:' + command
        return self.Exchange(s, warn=warn)
        # Add error catching


    def Set_direct(self, command, query=True, warn=True):
        '''Sends set command to main board and returns response string'''
        if query:
            if not messagebox.askyesno(APP_NAME,
                    'Would you like to "SET:'+command+'" ?'):
                return None
        s = 'SET:' + command
        return self.Exchange(s, warn=warn)
        # Add error catching



def List_ports():
    '''Returns a list of the found comports'''
    A = serial.tools.list_ports.comports()
    return [i.device for i in A]



class Ports():
    '''
    Class that holds reference to all the acessible ports
    And the functions for calling the desired variables?
    '''

    def __init__(self):
        '''Finds all ports and builds the iTC and iPS classes'''
        # Create empty ips and itc slot
        self.ips = None
        self.itc = None

        ports = List_ports()

        for port in ports:
            p = Comport(port)
            s = p.Identify()
            split = s.split(':')
            
            if len(split) < 3:
                logger.info('Found port: '+ port)
            elif split[2] == 'MERCURY IPS':
                self.ips = Mercury(port)
                logger.info('Found IPS:'+ port)
                self.ips.Find_daughters()
                self.ips.Build_daughters()
            elif split[2] == 'MERCURY ITC':
                self.itc = Mercury(port)
                self.itc.Find_daughters()
                logger.info('Found ITC:'+ port)
                self.itc.Build_daughters()
            else:
                logger.info('Found port: '+ port)

        # Warn if devices were not found
        if self.ips == None:
            logger.info('IPS not found!')
            messagebox.showerror('Missing IPS',
                'IPS not found, enable remote control and restart program')

        if self.itc == None:
            logger.info('ITC not found!')
            messagebox.showerror('Missing ITC',
                'ITC not found, enable remote control and restart program')

    def Get_T(self, sens2='DB4.G1'):
        temp_probe = self.itc.__dict__[sens2].Read_option('TEMP', warn=False)
        return temp_probe

    # iTC reading
    def Get_Tlog(self, sens, sens2='DB4.G1'):       # treba spremenit glede na komp probs(sens2)
        '''Gets the parameters required for logging without warnings'''
        time = datetime.now()
        temperature = self.itc.__dict__[sens].Read_option('TEMP', warn=False)
        setpoint = self.itc.__dict__[sens].Read_option('TSET', warn=False)
        heater = self.itc.__dict__[sens].Read_option('HSET', warn=False)
        flow = self.itc.__dict__[sens].Read_option('FLSET', warn=False)

        temp_probe = self.itc.__dict__[sens2].Read_option('TEMP', warn=False)

        return(time, setpoint, temperature, temp_probe, heater, flow)


    def Get_Tstatus(self, sens, htr):
        '''Gets the parameters required to update the status bar'''
        time = datetime.now()
        temperature = self.itc.__dict__[sens].Read_option('TEMP')
        setpoint = self.itc.__dict__[sens].Read_option('TSET')
        heater = self.itc.__dict__[sens].Read_option('HSET')
        flow = self.itc.__dict__[sens].Read_option('FLSET')
        power = self.itc.__dict__[htr].Read_option('POWR')

        return(time, temperature, setpoint, heater, flow, power)

    
    def Get_Tset(self, sens):
        ''' Gets the parameters required to update the set frame'''
        setpoint = self.itc.__dict__[sens].Read_option('TSET')
        ramp = self.itc.__dict__[sens].Read_option('RSET')
        ramp_enable = self.itc.__dict__[sens].Read_option('RENA')

        return(setpoint, ramp, ramp_enable)


    def Set_Tset(self, sens, values, query=True):
        '''Sets the parameters from the set frame
            values: (setpoint, ramp, ramp_enable)
            query=True Asks to confirm set values'''

        # When enabling ramp
        if values[2] == 'ON':
            # Check if current temperature is close to previous set point
            prev_setpoint = self.itc.__dict__[sens].Read_option('TSET')
            curr_temp = self.itc.__dict__[sens].Read_option('TEMP')
            # Strip units
            prev_setpoint = prev_setpoint[:-3]
            curr_temp = curr_temp[:-3]
            # Calculate difference
            new_ramp_rate = float(values[1])
            diff = abs(float(curr_temp) - float(prev_setpoint))

            if diff > new_ramp_rate:
                # Errors
                msg = '''The temperature has not reached previous setpoint.\n
                    Ramping from current temperature to new set point!'''
                messagebox.showerror('Ramping error', msg)
                logger.error('Temperature is not same as previous setpoint')

                # Make it go faster
                query = False
                # Change setpoint instantly to current temp, start ramping:
                self.itc.__dict__[sens].Set_option('RENA', 'OFF', query)
                self.itc.__dict__[sens].Set_option('TSET', curr_temp, query)
                # Continue by setting given: ramp on, ramp rate, new temp
        
        # First ramp rates, then temperature!
        # Check for errors. Probably can be omitted and done lower
        if not self.itc.__dict__[sens].Set_option('RENA', values[2], query):
            logger.error('Failed to set ramp to '+values[2])
        if not self.itc.__dict__[sens].Set_option('RSET', values[1], query):
            logger.error('Failed to set ramp rate to '+values[1])
        if not self.itc.__dict__[sens].Set_option('TSET', values[0], query):
            logger.error('Failed to set T to '+values[0])
    

    def Get_Tmanual(self, sens):
        '''Gets the parameters reqired to update the manual bar'''
        heater = self.itc.__dict__[sens].Read_option('HSET')
        flow = self.itc.__dict__[sens].Read_option('FLSET')
        heater_enable = self.itc.__dict__[sens].Read_option('ENAB')
        flow_enable = self.itc.__dict__[sens].Read_option('FAUT')

        return(heater, flow, heater_enable, flow_enable)


    def Get_Tloop(self, sens):
        '''Gets the parameters for the loop control frame'''
        p = self.itc.__dict__[sens].Read_option('P')
        i = self.itc.__dict__[sens].Read_option('I')
        d = self.itc.__dict__[sens].Read_option('D')
        htr = self.itc.__dict__[sens].Read_option('HTR')
        aux = self.itc.__dict__[sens].Read_option('AUX')

        return(p, i, d, htr, aux)


    def Get_Tlimits(self, sens, htr):
        '''Gets the parameters for heater limits frame'''
        heater_limit = self.itc.__dict__[htr].Read_option('VLIM')
        hot_limit = self.itc.__dict__[sens].Read_option('HOTL')
        cold_limit = self.itc.__dict__[sens].Read_option('COLDL')

        return(heater_limit, hot_limit, cold_limit)

    
    # iPS reading
    def Get_Flog(self, sens):
        '''Gets the parameters required for logging'''
        time = datetime.now()
        field = self.ips.__dict__[sens].Read_option('FLD', warn=False)
        field_set = self.ips.__dict__[sens].Read_option('FSET', warn=False)
        persist_field = self.ips.__dict__[sens].Read_option('PFLD', warn=False)

        return(time, field_set, field, persist_field)


    def Get_Fstatus(self, sens):
        '''Gets the parameters required to update the status bar'''
        time = datetime.now()
        field = self.ips.__dict__[sens].Read_option('FLD')
        field_set = self.ips.__dict__[sens].Read_option('FSET')
        voltage = self.ips.__dict__[sens].Read_option('VOLT')
        current = self.ips.__dict__[sens].Read_option('CURR')
        field_rate = self.ips.__dict__[sens].Read_option('RFLD')
        persistent_field = self.ips.__dict__[sens].Read_option('PFLD')

        return(time, field, field_set, voltage, current, field_rate,
            persistent_field)


    def Get_Fset(self, sens):
        '''Gets the parameters reguired to update the set field frame'''
        target_field = self.ips.__dict__[sens].Read_option('FSET')
        ramp_rate = self.ips.__dict__[sens].Read_option('RFST')

        return(target_field, ramp_rate)


    def Set_Fset(self, sens, values):
        '''Takes the field set and rate and sends them to the iPS
            values: (field_set, field_ramp_rate)'''
        if not self.ips.__dict__[sens].Set_option('RFST', values[1]):
            logger.error('Failed to set field ramp rate to '+values[1])
        if not self.ips.__dict__[sens].Set_option('FSET', values[0]):
            logger.error('Failed to set field rate to '+values[0])

    
    def Get_Fmode(self, sens):
        '''Gets parameters to update heater mode and ramp mode'''
        heater_mode = self.ips.__dict__[sens].Read_option('SWHT')
        ramp_mode = self.ips.__dict__[sens].Read_option('ACTN')

        return(heater_mode, ramp_mode)

    
    def Get_Fsensors(self, sens, lvl, temp):
        '''Gets parameters to update sensor status'''
        helium_bar = self.ips.__dict__[lvl].Read_option('HLEV')
        nitrogen_bar = self.ips.__dict__[lvl].Read_option('NLEV')
        #helium_res = self.ips.__dict__[lvl].Read_option('HRES')
        #nitrogen_fr = self.ips.__dict__[lvl].Read_option('FREQ')
        #temperature = self.ips.__dict__[temp].Read_option('TEMP')

        return(helium_bar, nitrogen_bar)


    def Get_Fsens(self, lvl):
        '''Gets parameters to update sensor status'''
        time = datetime.now()
        helium_bar = self.ips.__dict__[lvl].Read_option('HLEV', warn=False)
        nitrogen_bar = self.ips.__dict__[lvl].Read_option('NLEV', warn=False)

        return(time, helium_bar, nitrogen_bar)



if __name__ == "__main__":
    '''Executes if this is main application'''
    print(List_ports())
"""
    test = 0
    # Test particular port
    if test == 0:
        A=Mercury('COM4')
        A.Identify()
        print(A.Find_daughters(test=True))
        A.Build_daughters(test=True)

        print(A.__dict__)
        print('closing')
        print(A.ser.is_open)
        A.ser.close()

    # Test port importing
    if test == 1:
        B = Ports()
        print(B.__dict__)
        B.ips.Identify()
        print(B.ips.__dict__)
        x = B.ips.Find_daughters()
        print(x)
        B.ips.Build_daughters()
        print(B.ips.__dict__, '\n')

        print(B.ips.M2.__dict__)
        print(B.ips.M1.read_options)
        B.ips.M1.Read_option('VOLT')
"""

