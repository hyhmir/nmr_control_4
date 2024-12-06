import numpy as np
from func9 import No_Sffx, Integrate
import matplotlib.pyplot as plt


class avtomat():
    def __init__(self):
        self.frequ = []
        self.integral_complex = []
        self.integral_real = []


    def avto(self, gui, tecmag, figure1, figure2, figure3, a, perc, size, index, full, phc):
        params = {}

        params['Dwell Time'] = '2u'
        params['Acq. Points'] = '2048'

        for freq in np.linspace(93, 93.5, 8):
            params['Observe Freq.'] = str(freq) + 'MHz'
            tecmag.set_params(params)
            tecmag.Runandsave(figure1, figure2, figure3, a, perc, size, index, full, phc)
            gui.Write(str(tecmag.doc.GetNMRParameter('Observe Freq.')))

            self.frequ.append(freq)
            self.integral_real.append(Integrate(tecmag.data.real, stop=int(No_Sffx(params['Acq. Points'])), diff=No_Sffx(params['Dwell Time'])))

            print(self.frequ)

            # ax = figure3.add_subplot()
            # line, = ax.plot([])
            # line.set_xdata(self.frequ)
            # line.set_ydata(self.integral_real)
            # figure3.canvas.draw()
            # figure3.canvas.flush_events()


if __name__ == "__main__":
    print('hello')