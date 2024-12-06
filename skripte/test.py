import numpy as np
from func9 import No_Sffx, Integrate


class avtomat():
    def __init__(self):
        self.risi = {}
        self.frequ = []
        self.integral = []
        self.risi['freq'] = self.frequ
        self.risi['integral'] = self.integral

    def avto(self, gui, tecmag, figure1, figure2, a, perc, size, index, full, phc):
        params = {}

        params['Dwell Time'] = '2u'
        params['Acq. Points'] = '2048'

        for freq in np.linspace(93, 93.5, 8):
            params['Observe Freq.'] = str(freq) + 'MHz'
            tecmag.set_params(params)
            tecmag.Runandsave(figure1, figure2, a, perc, size, index, full, phc)
            gui.Write(str(tecmag.doc.GetNMRParameter('Observe Freq.')))

        
            # self.frequ.append(tecmag.doc.GetNMRParameter('Observe Freq.'))
            # self.integral.append(Integrate(tecmag.data.real, stop=int(No_Sffx(params['Acq. Points'])), diff=No_Sffx(params['Dwell Time'])))
            # self.risi['freq'] = self.frequ
            # self.risi['integral'] = self.integral
            # print(risi)


if __name__ == "__main__":
    print('hello')
