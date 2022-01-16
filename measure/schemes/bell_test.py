from loguru import logger
import numpy as np
from measure.scheme import BaseScheme
from utils.delays import DelayLines
import random

MEASURE_TIME = 1

WINDOW_SIZE = 12
MEASUREMENTS_PER_ITERATION = 10

CORRECTION_FACTOR = 0

CA_STEPS = 39
WA_STEPS = 88
CB_STEPS = 29
WB_STEPS = DelayLines.WB.calculate_steps(DelayLines.CB.calculate_delays(CB_STEPS) + WINDOW_SIZE)

ALPHA_ANGLES = 2 * np.array([-22.5, -22.5, -22.5, -22.5, 0, 0, 0, 0, 22.5, 22.5, 22.5, 22.5, 45, 45, 45, 45])
BETA_ANGLES = 2 * np.array([-11.25, 11.25, 33.75, 56.25, -11.25, 11.25, 33.75, 56.25, -11.25, 11.25, 33.75, 56.25,
                            -11.25, 11.25, 33.75, 56.25])

A_ARRAY = np.unique(ALPHA_ANGLES)
B_ARRAY = np.unique(BETA_ANGLES)

ITERATIONS = len(ALPHA_ANGLES)
# ITERATIONS = 10


class BellTest(BaseScheme):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, data_points=3, iterations=ITERATIONS, **kwargs)
        self.data: np.ndarray = np.zeros((ITERATIONS, 3, MEASUREMENTS_PER_ITERATION))

    @property
    def metadata(self) -> dict:
        metadata = super().metadata
        metadata.update({
            'CA_STEPS': CA_STEPS,
            'WA_STEPS': WA_STEPS,
            'CB_STEPS': CB_STEPS,
            'WB_STEPS': WB_STEPS,
            'correction_factor': CORRECTION_FACTOR,
            'measure_time': MEASURE_TIME,
            'measurements_per_iteration': MEASUREMENTS_PER_ITERATION,
            'iterations': ITERATIONS,
            'alpha_angles': ALPHA_ANGLES,
            'beta_angles': BETA_ANGLES
        })
        return metadata

    def setup(self):
        self.coincidence_circuit.set_delay(CA_STEPS, DelayLines.CA)
        self.coincidence_circuit.set_delay(WA_STEPS, DelayLines.WA)
        self.coincidence_circuit.set_delay(CB_STEPS, DelayLines.CB)
        self.coincidence_circuit.set_delay(WB_STEPS, DelayLines.WB)

    def iteration(self, i):
        for j in range(MEASUREMENTS_PER_ITERATION):
            self.data[i, :, j] = self.coincidence_circuit.measure(MEASURE_TIME)
            # self.data[i, :, j] = (random.random() * 1e6, random.random() * 1e6, random.random() * 1e6)
        logger.info(f'For α = {ALPHA_ANGLES[i]}° and β = {BETA_ANGLES[i]}°:')
        logger.info(f"Counter 1: {np.mean(self.data[i][0]):.1f} ± "
                    f"{np.std(self.data[i][0]) / np.sqrt(MEASUREMENTS_PER_ITERATION):.1f}")
        logger.info(f"Counter 2: {np.mean(self.data[i][1]):.1f} ± "
                    f"{np.std(self.data[i][1]) / np.sqrt(MEASUREMENTS_PER_ITERATION):.1f}")
        logger.info(f"Coincidences: {np.mean(self.data[i][2]):.1f} ± "
                    f"{np.std(self.data[i][2]) / np.sqrt(MEASUREMENTS_PER_ITERATION):.1f}")
        if i != ITERATIONS - 1:
            logger.info(f'Press enter to continue with α = {ALPHA_ANGLES[i + 1]}° and β = {BETA_ANGLES[i + 1]}°')
            input()

    @classmethod
    def analyse(cls, data, metadata):
        E_matrix = np.zeros((2, 2))
        for i in range(2):
            a = A_ARRAY[i]
            a_bot = A_ARRAY[i + 2]
            for j in range(2):
                b = B_ARRAY[j]
                b_bot = B_ARRAY[j + 2]
                index = np.where(np.logical_and(ALPHA_ANGLES == a, BETA_ANGLES == b))
                index_a_bot = np.where(np.logical_and(ALPHA_ANGLES == a_bot, BETA_ANGLES == b))
                index_b_bot = np.where(np.logical_and(ALPHA_ANGLES == a, BETA_ANGLES == b))
                index_bot = np.where(np.logical_and(ALPHA_ANGLES == a_bot, BETA_ANGLES == b_bot))
                E_matrix[i, j] = (np.mean(data[index, 2]) - np.mean(data[index_a_bot, 2]) - np.mean(
                                   data[index_b_bot, 2]) + np.mean(data[index_bot, 2])) / (
                                   np.mean(data[index, 2]) + np.mean(data[index_a_bot, 2])
                                   + np.mean(data[index_b_bot, 2]) + np.mean(data[index_bot, 2]))

        S_strong = np.abs(E_matrix[0, 0] + E_matrix[1, 1] - E_matrix[0, 1] + E_matrix[1, 0])
        S_weak = np.abs(E_matrix[0, 0] - E_matrix[0, 1]) + np.abs(E_matrix[1, 1] + E_matrix[1, 0])
        logger.info(f'S_strong = {S_strong}')
        logger.info(f'S_weak = {S_weak}')
        metadata.update({
            'E_matrix': E_matrix,
            'S_strong': S_strong,
            'S_weak':   S_weak
        })
