import tkinter as tk
import numpy as np
import mydaq


def sinus_window():
    # Toplevel object which will
    # be treated as a new window
    newWindow = tk.Toplevel(window)

    # sets the title of the
    # Toplevel widget
    newWindow.title("Sinus")

    # Input
    global rate_inp
    global samp_inp
    global amp_inp
    global freq_inp
    global phase_inp
    global offset_inp

    rate_inp = tk.Entry(newWindow)
    samp_inp = tk.Entry(newWindow)
    amp_inp = tk.Entry(newWindow)
    freq_inp = tk.Entry(newWindow)
    phase_inp = tk.Entry(newWindow)
    offset_inp = tk.Entry(newWindow)

    rate_lab = tk.Label(newWindow, text='Rate')
    samp_lab = tk.Label(newWindow, text='Samples')
    amp_lab = tk.Label(newWindow, text='Amplitude')
    freq_lab = tk.Label(newWindow, text='Frequency')
    phase_lab = tk.Label(newWindow, text='Phase')
    offset_lab = tk.Label(newWindow, text='Offset')

    run = tk.Button(newWindow, text='Run', command=sinus_button)

    rate_lab.pack()
    rate_inp.pack()
    samp_lab.pack()
    samp_inp.pack()
    amp_lab.pack()
    amp_inp.pack()
    freq_lab.pack()
    freq_inp.pack()
    phase_lab.pack()
    phase_inp.pack()
    offset_lab.pack()
    offset_inp.pack()
    run.pack()


def sinus_button():
    try:
        rate = float(rate_inp.get())
        samp = float(samp_inp.get())
        amp = float(amp_inp.get())
        freq = float(freq_inp.get())
        phase = float(phase_inp.get())
        offset = float(offset_inp.get())
        md.sine(rate, samp, amp, freq, phase, offset)
    except(ValueError):
        print('Vul getallen in a.u.b.')


def read_write_window():
    # Toplevel object which will
    # be treated as a new window
    global newWindow
    newWindow = tk.Toplevel(window)

    # sets the title of the
    # Toplevel widget
    newWindow.title("Read and write")

    # Input
    global array_lab
    global array_inp
    global rate_I_inp
    global rate_O_inp
    global samp_I_inp
    global samp_O_inp
    global data_var
    global plot_var
    global two_var
    global sin_var
    global run

    array_inp = tk.Entry(newWindow)
    rate_I_inp = tk.Entry(newWindow)
    rate_O_inp = tk.Entry(newWindow)
    samp_I_inp = tk.Entry(newWindow)
    samp_O_inp = tk.Entry(newWindow)

    data_var = tk.BooleanVar()
    plot_var = tk.BooleanVar()
    two_var = tk.BooleanVar()
    sin_var = tk.BooleanVar()

    data_inp = tk.Checkbutton(newWindow, text='Save data', command=save, variable=data_var)
    plot_inp = tk.Checkbutton(newWindow, text='Plot data', variable=plot_var)
    two_inp = tk.Checkbutton(newWindow, text='Measure both input channels.', variable=two_var)
    sin_inp = tk.Checkbutton(newWindow, text='Sinusoidal input', command=sin_inp_func, variable=sin_var)


    array_lab = tk.Label(newWindow, text='Array')
    rate_I_lab = tk.Label(newWindow, text='Rate I')
    rate_O_lab = tk.Label(newWindow, text='Rate O')
    samp_I_lab = tk.Label(newWindow, text='Samples I')
    samp_O_lab = tk.Label(newWindow, text='Samples O')

    run = tk.Button(newWindow, text='Run', command=read_write_button)

    array_lab.pack()
    array_inp.pack()
    rate_I_lab.pack()
    rate_I_inp.pack()
    rate_O_lab.pack()
    rate_O_inp.pack()
    samp_I_lab.pack()
    samp_I_inp.pack()
    samp_O_lab.pack()
    samp_O_inp.pack()
    data_inp.pack()
    plot_inp.pack()
    two_inp.pack()
    sin_inp.pack()
    run.pack()


def read_write_button():
    try:
        rate_I = float(rate_I_inp.get())
        rate_O = float(rate_O_inp.get())
        samp_I = float(samp_I_inp.get())
        samp_O = float(samp_O_inp.get())
        sinusoid = bool(sin_var.get())
        if sinusoid:
            amp = float(amp_inp.get())
            freq = float(freq_inp.get())
            phase = float(phase_inp.get())
            offset = float(offset_inp.get())
            time_array = np.linspace(0, samp_I, int(samp_I * rate_I))
            array = amp * np.sin(freq * 2 * np.pi * time_array + phase) + offset
        else:
            array = np.fromstring(array_inp.get(), sep=',')

        data = bool(data_var.get())
        plot = bool(plot_var.get())
        two = bool(two_var.get())
        if data:
            file = str(file_inp.get())
            dat, tim = md.read_write(array, rate_I, rate_O, samp_I, samp_O, True, True, plot, two)
            np.savetxt(f'{file}_data.txt', dat)
            np.savetxt(f'{file}_time.txt', tim)
        else:
            md.read_write(array, rate_I, rate_O, samp_I, samp_O, False, False, plot, two)
    except(ValueError):
        print('Vul correcte waarden in a.u.b.')


def read_window():
    # Toplevel object which will
    # be treated as a new window
    newWindow = tk.Toplevel(window)

    # sets the title of the
    # Toplevel widget
    newWindow.title("Read")

    # Input
    global rate_inp
    global samp_inp
    global time_var
    global data_var
    global plot_var
    global two_var

    rate_inp = tk.Entry(newWindow)
    samp_inp = tk.Entry(newWindow)

    time_var = tk.BooleanVar()
    data_var = tk.BooleanVar()
    plot_var = tk.BooleanVar()
    two_var = tk.BooleanVar()

    time_inp = tk.Checkbutton(newWindow, text='Return time array')
    data_inp = tk.Checkbutton(newWindow, text='Return data')
    plot_inp = tk.Checkbutton(newWindow, text='Plot data')
    two_inp = tk.Checkbutton(newWindow, text='Measure both input channels.')

    rate_lab = tk.Label(newWindow, text='Rate')
    samp_lab = tk.Label(newWindow, text='Samples')

    run = tk.Button(newWindow, text='Run', command=read_button)

    rate_lab.pack()
    rate_inp.pack()
    samp_lab.pack()
    samp_inp.pack()
    time_inp.pack()
    data_inp.pack()
    plot_inp.pack()
    two_inp.pack()
    run.pack()


def read_button():
    try:
        rate = float(rate_inp.get())
        samp = float(samp_inp.get())

        time = bool(time_var.get())
        data = bool(data_var.get())
        plot = bool(plot_var.get())
        two = bool(two_var.get())

        md.read_counts_from_register(rate, samp, time, data, plot, two)
    except(ValueError):
        print('Vul correcte waarden in a.u.b.')


def write_window():
    # Toplevel object which will
    # be treated as a new window
    newWindow = tk.Toplevel(window)

    # sets the title of the
    # Toplevel widget
    newWindow.title("Write")

    # Input
    global array_inp
    global rate_inp
    global samp_inp

    array_inp = tk.Entry(newWindow)
    rate_inp = tk.Entry(newWindow)
    samp_inp = tk.Entry(newWindow)

    array_lab = tk.Label(newWindow, text='Array')
    rate_lab = tk.Label(newWindow, text='Rate')
    samp_lab = tk.Label(newWindow, text='Samples')

    run = tk.Button(newWindow, text='Run', command=write_button)

    array_lab.pack()
    array_inp.pack()
    rate_lab.pack()
    rate_inp.pack()
    samp_lab.pack()
    samp_inp.pack()
    run.pack()


def write_button():
    try:
        array = np.fromstring(array_inp.get(), sep=',')
        rate = float(rate_inp.get())
        samp = float(samp_inp.get())

        md.write(array, rate, samp)
    except(ValueError):
        print('Vul correcte waarden in a.u.b.')


def sweep_window():
    # Toplevel object which will
    # be treated as a new window
    newWindow = tk.Toplevel(window)

    # sets the title of the
    # Toplevel widget
    newWindow.title("Spectrum sweep")

    # Input
    global f0_inp
    global f1_inp
    global indeces_inp
    global f_c_inp
    global rate_inp
    global samp_inp
    global amp_inp
    global file_inp

    f0_inp = tk.Entry(newWindow)
    f1_inp = tk.Entry(newWindow)
    indeces_inp = tk.Entry(newWindow)
    f_c_inp = tk.Entry(newWindow)
    rate_inp = tk.Entry(newWindow)
    samp_inp = tk.Entry(newWindow)
    amp_inp = tk.Entry(newWindow)
    file_inp = tk.Entry(newWindow)

    f0_lab = tk.Label(newWindow, text='f0')
    f1_lab = tk.Label(newWindow, text='f1')
    indeces_lab = tk.Label(newWindow, text='Indeces')
    f_c_lab = tk.Label(newWindow, text='f_c')
    rate_lab = tk.Label(newWindow, text='Rate')
    samp_lab = tk.Label(newWindow, text='Samples')
    amp_lab = tk.Label(newWindow, text='Amplitude')
    file_lab = tk.Label(newWindow, text='File name')

    run = tk.Button(newWindow, text='Run', command=sweep_button)

    f0_lab.pack()
    f0_inp.pack()
    f1_lab.pack()
    f1_inp.pack()
    indeces_lab.pack()
    indeces_inp.pack()
    f_c_lab.pack()
    f_c_inp.pack()
    rate_lab.pack()
    rate_inp.pack()
    samp_lab.pack()
    samp_inp.pack()
    amp_lab.pack()
    amp_inp.pack()
    file_lab.pack()
    file_inp.pack()
    run.pack()


def sweep_button():
    try:
        f0 = float(f0_inp.get())
        f1 = float(f1_inp.get())
        indeces = int(indeces_inp.get())
        f_c = eval(f_c_inp.get())
        rate = float(rate_inp.get())
        samp = float(samp_inp.get())
        amp = float(amp_inp.get())
        file = file_inp.get()

        mag, ang, freq = mydaq.spectrum_sweep(f0, f1, indeces, f_c, rate, samp, amp, md)
        np.savetxt(f'{file}_mag.txt', mag)
        np.savetxt(f'{file}_ang.txt', ang)
        np.savetxt(f'{file}_freq.txt', freq)

    except(ValueError):
        print('Vul correcte waarden in a.u.b.')


def save():
    if bool(data_var.get()):
        global file_inp
        global file_lab
        file_inp = tk.Entry(newWindow)
        file_lab = tk.Label(newWindow, text='File name')

        run.pack_forget()
        file_lab.pack()
        file_inp.pack()
        run.pack()

    else:
        file_lab.pack_forget()
        file_inp.pack_forget()


def sin_inp_func():
    if bool(sin_var.get()):
        global amp_inp
        global freq_inp
        global phase_inp
        global offset_inp

        global amp_lab
        global freq_lab
        global phase_lab
        global offset_lab

        amp_inp = tk.Entry(newWindow)
        freq_inp = tk.Entry(newWindow)
        phase_inp = tk.Entry(newWindow)
        offset_inp = tk.Entry(newWindow)

        amp_lab = tk.Label(newWindow, text='Amplitude')
        freq_lab = tk.Label(newWindow, text='Frequency')
        phase_lab = tk.Label(newWindow, text='Phase')
        offset_lab = tk.Label(newWindow, text='Offset')

        run.pack_forget()
        array_lab.pack_forget()
        array_inp.pack_forget()
        amp_lab.pack()
        amp_inp.pack()
        freq_lab.pack()
        freq_inp.pack()
        phase_lab.pack()
        phase_inp.pack()
        offset_lab.pack()
        offset_inp.pack()
        run.pack()
    else:
        array_lab.pack()
        array_inp.pack()
        amp_lab.pack_forget()
        amp_inp.pack_forget()
        freq_lab.pack_forget()
        freq_inp.pack_forget()
        phase_lab.pack_forget()
        phase_inp.pack_forget()
        offset_lab.pack_forget()
        offset_inp.pack_forget()

window = tk.Tk()

sin = tk.Button(window, text='Sinus', command=sinus_window)
rw = tk.Button(window, text='Read and Write', command=read_write_window)
read = tk.Button(window, text='Read', command=read_window)
write = tk.Button(window, text='Write', command=write_window)
sweep = tk.Button(window, text='Frequency sweep', command=sweep_window)

md = mydaq.MyDAQ()

sin.pack()
rw.pack()
read.pack()
write.pack()
sweep.pack()
window.mainloop()