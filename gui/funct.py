'''Supporting functions for gui class'''

def Strip_T(string):
    '''Reformats the temperature string'''
    try:
        return str(float(string[:-3]))
    except TypeError:
        return None


def List_sensors(name, mercury):
    '''Checks the mercury device for daughters with given name'''
    if mercury == None:
        print('Could not find device with daughters '+name)
        return []
    list_sens = []
    for daughter in mercury.daughters:
        split = daughter.split(':')
        if split[-1] == name:
            list_sens.append(split[0])
    return(list_sens)