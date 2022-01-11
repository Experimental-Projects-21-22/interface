import tkinter as tk
import random
# from loguru import logger
from interface import CoincidenceCircuit
from utils.delays import DelayLines

# Get around the max recursion depth
import sys
sys.setrecursionlimit(100000)

# tkinter stuff
font = ("Courier", 44)
root = tk.Tk()
tk.Label(root, text='Counter 1', font=font).grid(row=0, column=0)
tk.Label(root, text='Counter 2', font=font).grid(row=1, column=0)
tk.Label(root, text='Coincidences', font=font).grid(row=2, column=0)
lab_1 = tk.Label(root, font=font)
lab_2 = tk.Label(root, font=font)
lab_coinc = tk.Label(root, font=font)

lab_1.grid(row=0, column=1)
lab_2.grid(row=1, column=1)
lab_coinc.grid(row=2, column=1)

# Set constant values for delaylines
WINDOW_SIZE = 12
fixed_delay = 24
CORRECTION_FACTOR = 0

CA_steps = DelayLines.CA.calculate_steps(fixed_delay) + CORRECTION_FACTOR
WA_steps = DelayLines.WA.calculate_steps(fixed_delay + WINDOW_SIZE) + CORRECTION_FACTOR
CB_steps = DelayLines.CB.calculate_steps(fixed_delay)
WB_steps = DelayLines.WB.calculate_steps(fixed_delay + WINDOW_SIZE)

# Load circuit
coincidence_circuit = CoincidenceCircuit(baudrate=115200, port='/dev/tty.usbmodem142101')
coincidence_circuit.__enter__()

# Set the delays
coincidence_circuit.set_delay(CA_steps, DelayLines.CA)
coincidence_circuit.set_delay(WA_steps, DelayLines.WA)
coincidence_circuit.set_delay(CB_steps, DelayLines.CB)
coincidence_circuit.set_delay(WB_steps, DelayLines.WB)


def measure_rate():
    # Function that continuously measures the rate

    # Measure for 2 seconds
    measurement = coincidence_circuit.measure(1)
    # measurement = (random.random() * 1e6, random.random() * 1e6, random.random() * 1e6)
    # Split the measurements and convert to Hz
    counts_1 = f'{measurement[0]:.2E}'
    counts_2 = f'{measurement[1]:.2E}'
    counts_coinc = f'{measurement[2]:.2E}'

    # Update the labels
    lab_1.config(text=counts_1)
    lab_2.config(text=counts_2)
    lab_coinc.config(text=counts_coinc)

    root.after(1000, measure_rate) # Runs itself again after 1000 milliseconds


# start the loop
measure_rate()

root.mainloop()
