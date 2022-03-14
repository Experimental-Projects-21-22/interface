"""
Written by:
    Julian van Doorn <j.c.b.van.doorn@umail.leidenuniv.nl>
    Douwe Remmelts <remmeltsdouwe@gmail.com>
"""

import sys
import time
import tkinter as tk

from interface import CoincidenceCircuit
from utils.delays import DelayLines

# Get around the max recursion depth
sys.setrecursionlimit(100000)

# tkinter stuff
font = ("Courier", 70)
root = tk.Tk()

lab_1 = tk.Label(root, font=font)
lab_2 = tk.Label(root, font=font)
lab_coinc = tk.Label(root, font=font)
lab_rel = tk.Label(root, font=font)

# Set constant values for delaylines
WINDOW_SIZE = 12
fixed_delay = 24
CORRECTION_FACTOR = 0
MEASURE_TIME = 1

# CA_steps = DelayLines.CA.calculate_steps(fixed_delay) + CORRECTION_FACTOR
CA_steps = 37
# WA_steps = DelayLines.WA.calculate_steps(fixed_delay + WINDOW_SIZE) + CORRECTION_FACTOR
WA_steps = 86
# CB_steps = DelayLines.CB.calculate_steps(fixed_delay)
CB_steps = 29
WB_steps = 76

# Load circuit
coincidence_circuit = CoincidenceCircuit(baudrate=115200, port='/dev/cu.usbmodem14301')
coincidence_circuit.__enter__()
time.sleep(1)

# Set the delays
coincidence_circuit.set_delay(CA_steps, DelayLines.CA)
coincidence_circuit.set_delay(WA_steps, DelayLines.WA)
coincidence_circuit.set_delay(CB_steps, DelayLines.CB)
coincidence_circuit.set_delay(WB_steps, DelayLines.WB)

counts_1_values = []
counts_2_values = []
counts_coinc_values = []


def start_function():
    start_button.destroy()

    tk.Label(root, text='Counter 1', font=font).grid(row=0, column=0)
    tk.Label(root, text='Counter 2', font=font).grid(row=1, column=0)
    tk.Label(root, text='Coincidences', font=font).grid(row=2, column=0)
    tk.Label(root, text='Relative coincidences', font=font).grid(row=3, column=0)

    lab_1.grid(row=0, column=1)
    lab_2.grid(row=1, column=1)
    lab_coinc.grid(row=2, column=1)
    lab_rel.grid(row=3, column=1)

    measure_rate()


def measure_rate():
    # Function that continuously measures the rate

    # Measure for 2 seconds
    measurement = coincidence_circuit.measure(1)
    # measurement = (random.random() * 1e6, random.random() * 1e6, random.random() * 1e6)
    # Split the measurements and convert to Hz

    global counts_1_values, counts_2_values, counts_coinc_values
    counts_1_values.append(measurement[0])
    counts_2_values.append(measurement[1])
    counts_coinc_values.append(measurement[2])

    if len(counts_1_values) > MEASURE_TIME:
        counts_1_values.pop(0)
        counts_2_values.pop(0)
        counts_coinc_values.pop(0)

    if len(counts_1_values) == MEASURE_TIME:
        counts_1 = f'{sum(counts_1_values) / MEASURE_TIME:.2E} /s'
        counts_2 = f'{sum(counts_2_values) / MEASURE_TIME:.2E} /s'
        counts_coinc = f'{sum(counts_coinc_values) / MEASURE_TIME:.2E} /s'
        try:
            relative = f'{MEASURE_TIME * sum(counts_coinc_values) / (sum(counts_1_values) * sum(counts_2_values)):.2E}'
        except ZeroDivisionError:
            relative = 'Division by zero'
        # Update the labels
        lab_1.config(text=counts_1)
        lab_2.config(text=counts_2)
        lab_coinc.config(text=counts_coinc)
        lab_rel.config(text=relative)
    coincidence_circuit.reset_input_buffer()
    root.after(1000, measure_rate)  # Runs itself again after 1000 milliseconds


start_button = tk.Button(root, text='Start', font=font, command=start_function)
start_button.pack()
time.sleep(1)
# start the loop

root.mainloop()
