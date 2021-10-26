# A probably unnecessary GUI for the interface code

import tkinter as tk
import interface as Inf
from tkinter import messagebox

# Create fake serial port for testing
import os
import pty
master, slave = pty.openpty()
test = os.ttyname(slave)


def increase_command():
    # Command to get values from elements to be used in increasing the delay
    d0 = bool(check_var0.get())
    d1 = bool(check_var1.get())
    d2 = bool(check_var2.get())
    d3 = bool(check_var3.get())

    if d0 or d1 or d2 or d3:
        lines_bool = [d0, d1, d2, d3]
        try:
            steps = int(increments_entry.get())
            Coinc.increment(steps, lines_bool)
        except ValueError:
            messagebox.showerror('Python Error', 'Error: Please enter an integer number of increments')
    else:
        messagebox.showerror('Python Error', 'Error: Please select at least one delay line')


def coincidence_window():
    # Creates a window in which all coincidence circuit commands can be run

    # Establish global variables for data entry
    global check_var0
    global check_var1
    global check_var2
    global check_var3
    global increments_entry

    # Create a new window
    new_window = tk.Toplevel(window)

    # sets the title of the
    # Toplevel widget
    new_window.title("Coincidence circuit controls")

    counter_lab = tk.Label(new_window, text='Counter commands', font='Helvetica 18 bold')
    delay_lab = tk.Label(new_window, text='Delay line commands', font='Helvetica 18 bold')

    # Create buttons for all counter commands
    clear_but = tk.Button(new_window, text='Clear counter chips', command=Coinc.clear_counters)
    save_but = tk.Button(new_window, text='Save counts to registers', command=Coinc.save_counts_to_register)
    read_but = tk.Button(new_window, text='Read counter registers', command=Coinc.read_counts_from_register)
    save_read_but = tk.Button(new_window, text='Save and read_counts_from_register counter chips', command=Coinc.save_and_read_counts)

    # Create buttons for delay line commands
    check_lab = tk.Label(new_window, text='On which delay lines should the command be performed?', font='Helvetica 12 '
                                                                                                        'bold')
    increments_lab = tk.Label(new_window, text='Number of increments', font='Helvetica 12 bold')

    check_var0 = tk.IntVar()
    check_var1 = tk.IntVar()
    check_var2 = tk.IntVar()
    check_var3 = tk.IntVar()
    check_line0 = tk.Checkbutton(new_window, text='Line 0', var=check_var0)
    check_line1 = tk.Checkbutton(new_window, text='Line 1', var=check_var1)
    check_line2 = tk.Checkbutton(new_window, text='Line 2', var=check_var2)
    check_line3 = tk.Checkbutton(new_window, text='Line 3', var=check_var3)

    increments_entry = tk.Entry(new_window)

    increase_but = tk.Button(new_window, text='Increase the delay', command=increase_command)

    # Pack all elements
    counter_lab.grid(row=0, column=0, padx=100)
    clear_but.grid(row=1, column=0, padx=100)
    save_but.grid(row=2, column=0, padx=100)
    read_but.grid(row=3, column=0, padx=100)
    save_read_but.grid(row=4, column=0, padx=100)

    delay_lab.grid(row=0, column=1, columnspan=3)
    check_lab.grid(row=1, column=1, columnspan=2)
    check_line0.grid(row=2, column=1)
    check_line1.grid(row=2, column=2)
    check_line2.grid(row=3, column=1)
    check_line3.grid(row=3, column=2)

    increments_lab.grid(row=1, column=3)
    increments_entry.grid(row=2, column=3)

    increase_but.grid(row=4, column=1)


# Create objects for both arduino's
Coinc = Inf.CoincidenceCircuit(test)
Coinc.ser.open()
Step = Inf.Interferometer(test)
Step.ser.open()
# Create the GUI
window = tk.Tk()

coinc_but = tk.Button(window, text='Coincidence circuit commands', command=coincidence_window)

coinc_but.pack()

window.mainloop()
