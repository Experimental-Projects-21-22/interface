import time

import numpy as np
from loguru import logger
from matplotlib import pyplot as plt

from interface import CoincidenceCircuit, DELAY_LINES, DELAY_STEPS, DELAY_STEP_SIZE, Interferometer

# Arrays to store our data
delays = np.arange(0, DELAY_STEPS * DELAY_STEP_SIZE, DELAY_STEP_SIZE)
counts1 = np.zeros((DELAY_STEPS,))
counts2 = np.zeros((DELAY_STEPS,))
coincidences = np.zeros((DELAY_STEPS,))

with CoincidenceCircuit(baudrate=115200, port='/dev/cu.usbmodem14301') as coincidence_circuit, \
        Interferometer(baudrate=115200, port='/dev/cu.usbmodem14301') as interferometer:
    # Set the interferometer to a known state.
    interferometer.set_rotation(0)

    # Set the coincidence circuit to its initial state.
    coincidence_circuit.toggle_verbose()
    for delay_line in DELAY_LINES:
        coincidence_circuit.set_delay(0, delay_line)

    # Delay 1s to give the Arduino time to process the flood of commands.
    logger.info("Delaying measurement for 1 second...")
    time.sleep(1)
    logger.info("Starting measurement!")

    # Run a loop to do the actual measurements
    for i in range(0, DELAY_STEPS):
        # Set the desired state
        coincidence_circuit.set_delay(i, 'WA')
        coincidence_circuit.set_delay(i, 'CA')
        coincidence_circuit.clear_counters()

        # Wait for the data to be acquired.
        time.sleep(0.5)

        # Obtain the data
        counts1[i], counts2[i], coincidences[i] = coincidence_circuit.save_and_read_counts()

g2 = coincidences / (counts1 * counts2)

plt.plot(delays, g2)
plt.xlabel(r"$\tau$ (ns)")
plt.ylabel(r"$g^2(\tau)$")
plt.show()
