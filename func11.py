##############################################################################
#  modul globalnih funkcij                                                   #
##############################################################################
import numpy as np
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tkinter as tk
import time


suffixes_dict = {'u': 1E-6, 'm': 1E-3, 'n': 1E-9, 'M': 1E6}

# Refresh clock - can be set for quicker or slower refresh rate
MEAS_LOOP_TIME = 0.01


def No_Sffx(str_num):  # Convert string numbers with suffixes to floats
    str_num = str(str_num)
    str_num = str_num.replace(' ', '')
    str_num = str_num.replace('Hz', '')
    if str_num[-1] in suffixes_dict:
        for k, v in suffixes_dict.items():
            if str_num[-1] == k:
                return float(str_num[:-1]) * v
    else:
        return float(str_num)


def To_Cpx(sez):  # naredi seznam kompleksnih stevil
    sez = np.array(sez)
    re = sez[::2]
    im = sez[1::2]
    return re + 1.j * im


def Numify(string):
    par = string.strip().split(' ')
    return par


def Paramify(string):
    par = string.strip().split('=')
    return par


def BaselineCorr(list, perc):
    perc = round(perc, 17)
    if perc == 0:
        return list
    if perc >= 1:
        return list - np.average(list)
    else:
        return list - np.average(list[len(list):int((len(list)) * (1 - perc) - 1):-1])


def LeftShift(list, index, full):
    if full:
        return np.roll(list, len(list) - index)
    if not full:
        return np.pad(list[index:], (0, index), 'constant', constant_values=(0, 0))


def ReSize(list, size):
    return np.pad(list, (0, size - len(list)), 'constant', constant_values=(0, 0))


def Integrate(list, start=0, stop=-1, diff=1):
    return np.trapezoid(list[start:stop], dx=diff)


def my_import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def T1(gui, plot, seq, od, do, kolk, label, path, intod, intdo):        #argumenti kot pri avto + plot=figure, (of,dw,ap)=glej params, seq=pulzna sekvenca, label kot avtoploti, path=kam shranjuje, intod, intdo=integral meje
    if hasattr(gui, 'line_last'):
        gui.line_last.remove()
    gui.tecmag.app.LoadSequence(seq)
    gui.axT1 = plot.add_subplot()
    gui.line_last = gui.figure5.gca().axvline(x=No_Sffx(gui.diks['Last Delay'].get()))
    og = gui.diks['d5'].get()
    r = (do/od)**(1/(kolk-1))
    listd5 = []
    for i in range(kolk):
        listd5.append(od*r**i)
    rng = np.random.default_rng()
    if gui.varshuffleT1.get():
        rng.shuffle(listd5)
    gui.arrd5 = []
    gui.integralT1_real = []
    gui.integralT1_imag = []
    # gui.axT1 = plot.add_subplot()
    listd5 = np.array(listd5)

    for d5 in listd5:
        label.config(text=(str(round(d5*1e6)) + 'u'))
        gui.diks['d5'].delete(0, tk.END)
        gui.diks['d5'].insert(0, str(round(d5*1e6)) + 'u')

        gui.tecmag.dict_Sequence['d5'] = str(round(d5*1e6)) + 'u'

        gui.tecmag.set_params()
        gui.tecmag.Runandsave(gui)
        gui.arrd5.append(No_Sffx(gui.tecmag.doc.GetNMRParameter('d5')))
        gui.integralT1_real.append(Integrate(gui.tecmag.data.real, start=intod, stop=intdo, diff=No_Sffx(gui.diks['Dwell Time'].get())))
        gui.integralT1_imag.append(Integrate(gui.tecmag.data.imag, start=intod, stop=intdo, diff=No_Sffx(gui.diks['Dwell Time'].get())))
        num = str(len(gui.arrd5))
        while len(num) != 3:
            num = "0" + num
        gui.Write(gui.T1_selected_directory.get() + '\\' + gui.T1_name.get() + "-" + num)
        gui.Write_integrals(gui.T1_selected_directory.get(), gui.T1_name.get() + "-g", gui.arrd5, gui.integralT1_real, gui.integralT1_imag, gui.arrd5)
        plot.clf()
        gui.axT1 = plot.add_subplot()
        gui.axT1.grid()
        gui.axT1.set_xscale('log')
        gui.axT1.scatter(gui.arrd5, gui.integralT1_real, color='magenta', marker='o', linestyle='--')
        gui.axT1.scatter(gui.arrd5, gui.integralT1_imag, color='lime', marker='o', linestyle='--')
        gui.line_last = gui.figure5.gca().axvline(x=No_Sffx(gui.diks['Last Delay'].get()))
        plot.canvas.draw()
        plot.canvas.flush_events()

    label.config(text='konec eksperimenta')
    gui.diks['d5'].delete(0, tk.END)
    gui.diks['d5'].insert(0, og)

    gui.tecmag.dict_Sequence['d5'] = og


def T1repete(gui, plot, seq, od, r, kolk, label, path, intod, intdo):
    og = gui.diks['d5'].get()
    listd5 = []
    for i in range(kolk):
        listd5.append(od*r**(i + 1))
    rng = np.random.default_rng()
    if gui.varshuffleT1.get():
        rng.shuffle(listd5)

    for d5 in listd5:
        label.config(text=(str(round(d5*1e6)) + 'u'))
        gui.diks['d5'].delete(0, tk.END)
        gui.diks['d5'].insert(0, str(round(d5*1e6)) + 'u')

        gui.tecmag.dict_Sequence['d5'] = str(round(d5*1e6)) + 'u'

        gui.tecmag.set_params()
        gui.tecmag.Runandsave(gui)
        gui.arrd5.append(No_Sffx(gui.tecmag.doc.GetNMRParameter('d5')))
        gui.integralT1_real.append(Integrate(gui.tecmag.data.real, start=intod, stop=intdo, diff=No_Sffx(gui.diks['Dwell Time'].get())))
        gui.integralT1_imag.append(Integrate(gui.tecmag.data.imag, start=intod, stop=intdo, diff=No_Sffx(gui.diks['Dwell Time'].get())))
        num = str(len(gui.arrd5))
        while len(num) != 3:
            num = "0" + num
        gui.Write(gui.T1_selected_directory.get() + '\\' + gui.T1_name.get() + "-" + num)
        gui.Write_integrals(gui.T1_selected_directory.get(), gui.T1_name.get() + "-g", gui.arrd5, gui.integralT1_real, gui.integralT1_imag, gui.arrd5)
        plot.clf()
        gui.axT1 = plot.add_subplot()
        gui.axT1.grid()
        gui.axT1.set_xscale('log')
        gui.axT1.scatter(gui.arrd5, gui.integralT1_real, color='magenta', marker='o', linestyle='--')
        gui.axT1.scatter(gui.arrd5, gui.integralT1_imag, color='lime', marker='o', linestyle='--')
        plot.canvas.draw()
        plot.canvas.flush_events()

    label.config(text='konec eksperimenta')
    gui.diks['d5'].delete(0, tk.END)
    gui.diks['d5'].insert(0, og)

    gui.tecmag.dict_Sequence['d5'] = og


def T2(gui, plot, seq, od, do, interval, label, path, intod, intdo):
    gui.tecmag.app.LoadSequence(seq)
    og = gui.diks['tau'].get()
    listtau = np.arange(od, do, interval)
    rng = np.random.default_rng()
    if gui.varshuffleT2.get():
        rng.shuffle(listtau)
    gui.arrtau = []
    gui.integralT2_real = []
    gui.integralT2_imag = []
    # gui.axT2 = plot.add_subplot()
    listtau = np.array(listtau)
    print(listtau)
    for tau in listtau:
        print(tau)
        label.config(text=(str(round(tau*1e6)) + 'u'))
        gui.diks['tau'].delete(0, tk.END)
        gui.diks['tau'].insert(0, str(round(tau*1e6)) + 'u')

        gui.tecmag.dict_Sequence['tau'] = str(round(tau*1e6)) + 'u'

        # gui.tecmag.app.LoadSequence(seq)
        gui.tecmag.set_params()
        gui.tecmag.Runandsave(gui)
        gui.arrtau.append(No_Sffx(gui.tecmag.doc.GetNMRParameter('tau')))
        gui.integralT2_real.append(Integrate(gui.tecmag.data.real, start=intod, stop=intdo, diff=No_Sffx(gui.diks['Dwell Time'].get())))
        gui.integralT2_imag.append(Integrate(gui.tecmag.data.imag, start=intod, stop=intdo, diff=No_Sffx(gui.diks['Dwell Time'].get())))
        num = str(len(gui.arrtau))
        while len(num) != 3:
            num = "0" + num
        gui.Write(gui.T2_selected_directory.get() + '\\' + gui.T2_name.get() + "-" + num)
        gui.Write_integrals(gui.T2_selected_directory.get(), gui.T2_name.get() + "-g", gui.arrtau, gui.integralT2_real, gui.integralT2_imag, gui.arrtau)
        plot.clf()
        gui.axT2 = plot.add_subplot()
        try:
            gui.axT2.set_yscale('log')
        except:
            gui.axT2.set_yscale('linear')
        gui.axT2.grid()
        gui.axT2.scatter(gui.arrtau, gui.integralT2_real, color='magenta', marker='o', linestyle='--')
        gui.axT2.scatter(gui.arrtau, gui.integralT2_imag, color='lime', marker='o', linestyle='--')
        plot.canvas.draw()
        plot.canvas.flush_events()

    label.config(text='konec eksperimenta')
    gui.diks['tau'].delete(0, tk.END)
    gui.diks['tau'].insert(0, og)

    gui.tecmag.dict_Sequence['tau'] = og


def T2repete(gui, plot, seq, od, interval, kolk, label, path, intod, intdo):
    og = gui.diks['tau'].get()
    listtau = []
    for i in range(kolk):
        listtau.append(od + interval * (i + 1))
    rng = np.random.default_rng()
    if gui.varshuffleT2.get():
        rng.shuffle(listtau)

    listtau = np.array(listtau)
    for tau in listtau:
        label.config(text=(str(round(tau*1e6)) + 'u'))
        gui.diks['tau'].delete(0, tk.END)
        gui.diks['tau'].insert(0, str(round(tau*1e6)) + 'u')

        gui.tecmag.dict_Sequence['tau'] = str(round(tau*1e6)) + 'u'

        gui.tecmag.set_params()
        gui.tecmag.Runandsave(gui)
        gui.arrtau.append(No_Sffx(gui.tecmag.doc.GetNMRParameter('tau')))
        gui.integralT2_real.append(Integrate(gui.tecmag.data.real, start=intod, stop=intdo, diff=No_Sffx(gui.diks['Dwell Time'].get())))
        gui.integralT2_imag.append(Integrate(gui.tecmag.data.imag, start=intod, stop=intdo, diff=No_Sffx(gui.diks['Dwell Time'].get())))
        num = str(len(gui.arrtau))
        while len(num) != 3:
            num = "0" + num
        gui.Write(gui.T2_selected_directory.get() + '\\' + gui.T2_name.get() + "-" + num)
        gui.Write_integrals(gui.T2_selected_directory.get(), gui.T2_name.get() + "-g", gui.arrtau, gui.integralT2_real, gui.integralT2_imag, gui.arrtau)
        plot.clf()
        gui.axT2 = plot.add_subplot()
        try:
            gui.axT2.set_yscale('log')
        except:
            gui.axT2.set_yscale('linear')
        gui.axT2.grid()
        gui.axT2.scatter(gui.arrtau, gui.integralT2_real, color='magenta', marker='o', linestyle='--')
        gui.axT2.scatter(gui.arrtau, gui.integralT2_imag, color='lime', marker='o', linestyle='--')
        plot.canvas.draw()
        plot.canvas.flush_events()

    label.config(text='konec eksperimenta')
    gui.diks['tau'].delete(0, tk.END)
    gui.diks['tau'].insert(0, og)

    gui.tecmag.dict_Sequence['tau'] = og


def sweep(gui, plot, seq, od, do, interval, label, path, intod, intdo):
    gui.tecmag.app.LoadSequence(seq)
    og = gui.diks['Observe Freq.'].get()
    listfreq = np.arange(od, do, interval)
    gui.arrfreq = []
    gui.integralsweep_real = []
    gui.integralsweep_imag = []
    gui.tempsweep = []
    # gui.axsweep = plot.add_subplot()

    for freq in listfreq:
        label.config(text=(str(freq/1E6) + 'MHz'))
        gui.diks['Observe Freq.'].delete(0, tk.END)
        gui.diks['Observe Freq.'].insert(0, str(freq/1E6) + 'MHz')
        gui.setfreq2('placeholdervar')

        gui.tecmag.dict_Acquisition['Observe Freq.'] = str(freq/1E6) + 'MHz'
        gui.tecmag.dict_Frequency['Observe Freq.'] = str(freq/1E6) + 'MHz'
        gui.tecmag.dict_Frequency['F1 Freq.'] = str(freq/1E6) + 'MHz'

        # gui.tecmag.app.LoadSequence(seq)
        gui.tecmag.set_params()
        gui.tecmag.Runandsave(gui)
        gui.arrfreq.append(No_Sffx(gui.tecmag.doc.GetNMRParameter('Observe Freq.')))
        gui.integralsweep_real.append(Integrate(gui.tecmag.data.real, start=intod, stop=intdo, diff=No_Sffx(gui.diks['Dwell Time'].get())))
        gui.integralsweep_imag.append(Integrate(gui.tecmag.data.imag, start=intod, stop=intdo, diff=No_Sffx(gui.diks['Dwell Time'].get())))
        gui.tempsweep.append(gui.getT())
        num = str(len(gui.arrfreq))
        while len(num) != 3:
            num = "0" + num
        gui.Write(gui.sweep_selected_directory.get() + '\\' + gui.sweep_name.get() + "-" + num)
        gui.Write_integrals(gui.sweep_selected_directory.get(), gui.sweep_name.get() + "-g", gui.arrfreq, gui.integralsweep_real, gui.integralsweep_imag, gui.tempsweep)
        plot.clf()
        gui.axsweep = plot.add_subplot()
        gui.axsweep.grid()
        gui.axsweep.plot(gui.arrfreq, gui.integralsweep_real, color='magenta', marker='o', linestyle='--')
        gui.axsweep.plot(gui.arrfreq, gui.integralsweep_imag, color='lime', marker='o', linestyle='--')
        plot.canvas.draw()
        plot.canvas.flush_events()

    label.config(text='konec eksperimenta')
    gui.diks['Observe Freq.'].delete(0, tk.END)
    gui.diks['Observe Freq.'].insert(0, og)
    gui.setfreq2('placeholdervar')

    gui.tecmag.dict_Acquisition['Observe Freq.'] = og
    gui.tecmag.dict_Frequency['Observe Freq.'] = og
    gui.tecmag.dict_Frequency['F1 Freq.'] = og

    if gui.check_notify_var.get():
        send_email(gui.user_mail.get(), 'Konec eksperimenta', 'Vašega eksperimenta je konec, akvizicija je potekala brez zapletov.')

def Sweeprepete(gui, plot, seq, od, interval, kolk, label, path, intod, intdo):
    og = gui.diks['Observe Freq.'].get()
    listfreq = []
    for i in range(kolk):
        listfreq.append(od + interval * (i + 1))
    
    for freq in listfreq:
        label.config(text=(str(freq/1E6) + ' MHz'))
        gui.diks['Observe Freq.'].delete(0, tk.END)
        gui.diks['Observe Freq.'].insert(0, (str(freq/1E6)))
        gui.setfreq2('placeholdervar')

        gui.tecmag.dict_Acquisition['Observe Freq.'] = str(freq/1E6) + 'MHz'
        gui.tecmag.dict_Frequency['Observe Freq.'] = str(freq/1E6) + 'MHz'
        gui.tecmag.dict_Frequency['F1 Freq.'] = str(freq/1E6) + 'MHz'

        # gui.tecmag.app.LoadSequence(seq)
        gui.tecmag.set_params()
        gui.tecmag.Runandsave(gui)
        gui.arrfreq.append(No_Sffx(gui.tecmag.doc.GetNMRParameter('Observe Freq.')))
        gui.integralsweep_real.append(Integrate(gui.tecmag.data.real, start=intod, stop=intdo, diff=No_Sffx(gui.diks['Dwell Time'].get())))
        gui.integralsweep_imag.append(Integrate(gui.tecmag.data.imag, start=intod, stop=intdo, diff=No_Sffx(gui.diks['Dwell Time'].get())))
        gui.tempsweep.append(gui.getT())
        # gui.Write(path + str(gui.tecmag.doc.GetNMRParameter('Observe Freq.')))
        num = str(len(gui.arrfreq))
        while len(num) != 3:
            num = "0" + num
        gui.Write(gui.sweep_selected_directory.get() + '\\' + gui.sweep_name.get() + "-" + num)
        gui.Write_integrals(gui.sweep_selected_directory.get(), gui.sweep_name.get() + "-g", gui.arrfreq, gui.integralsweep_real, gui.integralsweep_imag, gui.tempsweep)
        plot.clf()
        gui.axsweep = plot.add_subplot()
        gui.axsweep.grid()
        gui.axsweep.plot(gui.arrfreq, gui.integralsweep_real, color='magenta', marker='o', linestyle='--')
        gui.axsweep.plot(gui.arrfreq, gui.integralsweep_imag, color='lime', marker='o', linestyle='--')
        plot.canvas.draw()
        plot.canvas.flush_events()

    label.config(text='konec eksperimenta')
    gui.diks['Observe Freq.'].delete(0, tk.END)
    gui.diks['Observe Freq.'].insert(0, og)
    gui.setfreq2('placeholdervar')

    gui.tecmag.dict_Acquisition['Observe Freq.'] = og
    gui.tecmag.dict_Frequency['Observe Freq.'] = og
    gui.tecmag.dict_Frequency['F1 Freq.'] = og

def send_email(to_email, subject, message_body, from_email='nmr.status@ijs.si', password='mo.vrepro.vzadna'):
    try:
        # Set up the MIME
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add message body
        msg.attach(MIMEText(message_body, 'plain'))

        # Set up the SMTP server for Outlook
        server = smtplib.SMTP('mailbox.ijs.si', 587)
        server.starttls()  # Start TLS encryption
        server.login(from_email, password)

        # Send the email
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)

        # Close the connection to the SMTP server
        server.quit()

        print(f"Email sent successfully to {to_email}")

    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")

def FromXtoIndexFourier(x, dwelltime, acqpts):
    return round((x + (1 / (2e6 * dwelltime))) * 1e6 * dwelltime * acqpts)

def FromXtoIndexData(x, dwelltime):
    return round(x * 1e-3 / dwelltime)

def smooth(list):
    nov = np.zeros(len(list))
    for i in range(len(list)-1):
        a = np.average([list[i-1], list[i], list[i+1]])
        nov[i] = a
    nov[len(list)-1] = np.average([list[len(list)-2], list[len(list)-1], list[0]])
    return nov

def invers(slovar):
    return {v: k for k, v in slovar.items()}

if __name__ == '__main__':
    send_email('samo.krejan@gmail.com', 'test nmr', 'jou jou')

