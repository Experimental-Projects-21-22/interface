import time

from interface import DELAY_LINES
from .scheme import Scheme


class G2(Scheme):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, data_shape=(4, 5), iterations=5, **kwargs)

        self.counts1 = self.data[1]
        self.counts2 = self.data[2]
        self.coincidences = self.data[3]

    def setup(self):
        # Set the interferometer rotation to a known state.
        self.interferometer.set_rotation(0)
        # Set the coincidence circuit to its initial state.
        self.coincidence_circuit.toggle_verbose()
        for delay_line in DELAY_LINES:
            self.coincidence_circuit.set_delay(0, delay_line)

    def iteration(self, i):
        # Set the desired state
        self.coincidence_circuit.set_delay(i, 'WA')
        self.coincidence_circuit.set_delay(i, 'CA')
        self.coincidence_circuit.clear_counters()
        # Wait for the data to be acquired.
        time.sleep(0.5)
        # Obtain the data
        self.counts1[i], self.counts2[i], self.coincidences[i] = self.coincidence_circuit.save_and_read_counts()
