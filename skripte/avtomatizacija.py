# primer skripte za avtomatizacijo meritev
import numpy as np
from func10 import Integrate, No_Sffx

risi = {}
frequ = []
integral = []
risi['freq'] = frequ
risi['integral'] = integral


def avto(gui, tecmag):
    params = {}

    params['Dwell Time'] = '2u'
    params['Acq. Points'] = '2048'

    for freq in np.linspace(93, 93.5, 8):
        gui.avtoploti.config(text=str(freq))
        params['Observe Freq.'] = str(freq) + 'MHz'
        params['temp'] = gui.getT()
        tecmag.set_params(params)
        tecmag.Runandsave(gui)
        frequ.append(tecmag.doc.GetNMRParameter('Observe Freq.'))
        integral.append(Integrate(tecmag.data.real, stop=int(No_Sffx(params['Acq. Points'])), diff=No_Sffx(params['Dwell Time'])))
        gui.Write(str(tecmag.doc.GetNMRParameter('Observe Freq.')))
        gui.figure3.clf()
        gui.ax3 = gui.figure3.add_subplot()
        gui.ax3.scatter(frequ, integral)
        gui.figure3.canvas.draw()
        gui.figure3.canvas.flush_events()
        risi['freq'] = frequ
        risi['integral'] = integral

    gui.avtoploti.config(text='konec eksperimenta')



if __name__ == "__main__":
    print('hello')
