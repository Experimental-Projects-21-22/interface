from loguru import logger

from measure.scheme import BaseScheme
from utils.delays import DelayLines

MEASURE_TIME = 2

WINDOW_SIZE = 12
ITERATIONS = 1

CORRECTION_FACTOR = 2.3

LOWER_DELAY_LIMIT = 20
UPPER_DELAY_LIMIT = 80


class SingleRun(BaseScheme):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, data_points=3, iterations=ITERATIONS, **kwargs)

    @property
    def metadata(self) -> dict:
        metadata = super().metadata
        metadata.update({
            'window_size':       WINDOW_SIZE,
            'correction_factor': CORRECTION_FACTOR,
            'measure_time':      MEASURE_TIME,
            'lower_delay_limit': LOWER_DELAY_LIMIT,
        })
        return metadata

    def setup(self):
        self.coincidence_circuit.set_delay(DelayLines.CA.calculate_steps(LOWER_DELAY_LIMIT), DelayLines.CA)
        self.coincidence_circuit.set_delay(DelayLines.WA.calculate_steps(LOWER_DELAY_LIMIT + WINDOW_SIZE),
                                           DelayLines.WA)

        self.coincidence_circuit.set_delay(DelayLines.CB.calculate_steps(LOWER_DELAY_LIMIT - CORRECTION_FACTOR),
                                           DelayLines.CB)
        self.coincidence_circuit.set_delay(
            DelayLines.WB.calculate_steps(LOWER_DELAY_LIMIT + WINDOW_SIZE - CORRECTION_FACTOR), DelayLines.WB)

    def iteration(self, i):
        self.data[:, i] = self.coincidence_circuit.measure(MEASURE_TIME)

    @classmethod
    def analyse(cls, data, metadata):
        logger.info(f"Counts 1: {data[0][0]}")
        logger.info(f"Counts 2: {data[1][0]}")
        logger.info(f"Coincidences: {data[2][0]}")
