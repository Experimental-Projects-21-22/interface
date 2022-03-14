"""
Written by:
    Julian van Doorn <j.c.b.van.doorn@umail.leidenuniv.nl>
    Douwe Remmelts <remmeltsdouwe@gmail.com>
"""

import numpy as np
from loguru import logger

from measure.scheme import BaseScheme
from utils.delays import DelayLines

ITERATIONS = 10
MEASURE_TIME = 1

CA_steps = 61
WA_steps = 110
CB_steps = 37
WB_steps = 83


class SingleRun(BaseScheme):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, data_points=3, iterations=ITERATIONS, **kwargs)

    @property
    def metadata(self) -> dict:
        metadata = super().metadata
        metadata.update({
            'CA_steps':     CA_steps,
            'WA_steps':     WA_steps,
            'CB_steps':     CB_steps,
            'WB_steps':     WB_steps,
            'iterations':   ITERATIONS,
            'measure_time': MEASURE_TIME,
        })
        return metadata

    def setup(self):
        self.coincidence_circuit.set_delay(CA_steps, DelayLines.CA)
        self.coincidence_circuit.set_delay(WA_steps, DelayLines.WA)
        self.coincidence_circuit.set_delay(CB_steps, DelayLines.CB)
        self.coincidence_circuit.set_delay(WB_steps, DelayLines.WB)

    def iteration(self, i):
        self.data[:, i] = self.coincidence_circuit.measure(MEASURE_TIME)

    @classmethod
    def analyse(cls, data, metadata):
        logger.info(f"Counts 1: {np.mean(data[0])} ± {np.std(data[0]) / np.sqrt(ITERATIONS)}")
        logger.info(f"Counts 2: {np.mean(data[1])} ± {np.std(data[1]) / np.sqrt(ITERATIONS)}")
        logger.info(f"Coincidences: {np.mean(data[2])} ± {np.std(data[2]) / np.sqrt(ITERATIONS)}")
