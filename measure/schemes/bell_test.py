"""
Written by:
    Douwe Remmelts <remmeltsdouwe@gmail.com>
"""
import matplotlib.pyplot as plt
import numpy as np
from loguru import logger

from measure.scheme import BaseScheme
from utils.delays import DelayLines

MEASURE_TIME = 1

MEASUREMENTS_PER_ITERATION = 10

CA_STEPS = 37
WA_STEPS = 86
CB_STEPS = 29
WB_STEPS = 76

ALPHA_ANGLES = 2 * np.array([-22.5, -22.5, -22.5, -22.5, 0, 0, 0, 0, 22.5, 22.5, 22.5, 22.5, 45, 45, 45, 45])
BETA_ANGLES = 2 * np.array([-11.25, 11.25, 33.75, 56.25, 56.25, 33.75, 11.25, -11.25, -11.25, 11.25, 33.75, 56.25,
                            56.25, 33.75, -11.25, 11.25])

ALPHA_ZERO = 68
BETA_ZERO = 231

A_ARRAY = np.unique(ALPHA_ANGLES)
B_ARRAY = np.unique(BETA_ANGLES)
ITERATIONS = len(ALPHA_ANGLES)


# ITERATIONS = 10


def angle_transform(angle, alpha_bool=True):
    if alpha_bool:
        return angle / 2 + ALPHA_ZERO
    else:
        return angle / 2 + BETA_ZERO


def compute_E(N_pp_arr, N_mm_arr, N_pm_arr, N_mp_arr):
    """" Computes E for a given configuration of counts
    :param N_pp_arr: Array of values for N_++
    :param N_mm_arr: Array of values for N_--
    :param N_pm_arr: Array of values for N_+-
    :param N_mp_arr: Array of values for N_-+
    """
    N_pp, sigma_pp = np.mean(N_pp_arr), np.std(N_pp_arr) / np.sqrt(len(N_pp_arr))
    N_mm, sigma_mm = np.mean(N_mm_arr), np.std(N_mm_arr) / np.sqrt(len(N_mm_arr))
    N_pm, sigma_pm = np.mean(N_pm_arr), np.std(N_pm_arr) / np.sqrt(len(N_pm_arr))
    N_mp, sigma_mp = np.mean(N_mp_arr), np.std(N_mp_arr) / np.sqrt(len(N_mp_arr))

    norm_factor = N_pp + N_mm + N_pm + N_mp
    E = (N_pp + N_mm - N_pm - N_mp) / norm_factor
    sigma_E = 2 * np.sqrt(
        (N_pp + N_mm) ** 2 * (sigma_pm ** 2 + sigma_mp ** 2) + (N_pm + N_mp) ** 2 * (sigma_pp ** 2 + sigma_mm ** 2
                                                                                     )) / (norm_factor ** 2)
    return E, sigma_E


class BellTest(BaseScheme):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, data_points=3, iterations=1, **kwargs)
        self.data: np.ndarray = np.zeros((ITERATIONS, 3, MEASUREMENTS_PER_ITERATION))

    @property
    def metadata(self) -> dict:
        metadata = super().metadata
        metadata.update({
            'CA_steps':                   CA_STEPS,
            'WA_steps':                   WA_STEPS,
            'CB_steps':                   CB_STEPS,
            'WB_steps':                   WB_STEPS,
            'measure_time':               MEASURE_TIME,
            'measurements_per_iteration': MEASUREMENTS_PER_ITERATION,
            'iterations':                 ITERATIONS,
            'alpha_angles':               ALPHA_ANGLES,
            'beta_angles':                BETA_ANGLES
        })
        return metadata

    def setup(self):
        self.coincidence_circuit.set_delay(CA_STEPS, DelayLines.CA)
        self.coincidence_circuit.set_delay(WA_STEPS, DelayLines.WA)
        self.coincidence_circuit.set_delay(CB_STEPS, DelayLines.CB)
        self.coincidence_circuit.set_delay(WB_STEPS, DelayLines.WB)

    def iteration(self, _):
        i = 0
        i_old = 0
        logger.info(f'To start with ?? = {angle_transform(ALPHA_ANGLES[0])}?? and '
                    f'?? = {angle_transform(BETA_ANGLES[0], False)}??, press enter')
        input()
        while i < ITERATIONS:
            for j in range(MEASUREMENTS_PER_ITERATION):
                self.data[i, :, j] = self.coincidence_circuit.measure(MEASURE_TIME)
            logger.info(f'For ?? = {angle_transform(ALPHA_ANGLES[i])}?? and '
                        f'?? = {angle_transform(BETA_ANGLES[i], False)}?? ({i + 1} out of {ITERATIONS}):')
            logger.info(f"Counter 1: {np.mean(self.data[i][0]):.1f} ?? "
                        f"{np.std(self.data[i][0]) / np.sqrt(MEASUREMENTS_PER_ITERATION):.1f}")
            logger.info(f"Counter 2: {np.mean(self.data[i][1]):.1f} ?? "
                        f"{np.std(self.data[i][1]) / np.sqrt(MEASUREMENTS_PER_ITERATION):.1f}")
            logger.info(f"Coincidences: {np.mean(self.data[i][2]):.1f} ?? "
                        f"{np.std(self.data[i][2]) / np.sqrt(MEASUREMENTS_PER_ITERATION):.1f}")
            if i < i_old:
                i = i_old
            if i != ITERATIONS - 1:
                logger.info(f'Press enter to continue with ?? = {angle_transform(ALPHA_ANGLES[i + 1])}?? and'
                            f' ?? = {angle_transform(BETA_ANGLES[i + 1], False)}??'
                            f' ({i + 2} out of {ITERATIONS})\n'
                            f'If another iteration is desired, type this number followed by an enter instead')
            else:
                logger.info('If satisfied, press enter. Otherwise enter the iteration which you want to repeat')
            choice = input()
            if choice != '':
                i_old = i
                i = int(choice) - 1
            i += 1

    @classmethod
    def analyse(cls, data, metadata):
        E_matrix = np.zeros((2, 2))
        sigma_E_matrix = np.zeros((2, 2))
        for i in range(2):
            a = A_ARRAY[i]
            a_bot = A_ARRAY[i + 2]
            for j in range(2):
                b = B_ARRAY[j]
                print((angle_transform(a), angle_transform(b, False)), (i, j))
                b_bot = B_ARRAY[j + 2]
                index = np.where(np.logical_and(ALPHA_ANGLES == a, BETA_ANGLES == b))
                index_a_bot = np.where(np.logical_and(ALPHA_ANGLES == a_bot, BETA_ANGLES == b))
                index_b_bot = np.where(np.logical_and(ALPHA_ANGLES == a, BETA_ANGLES == b_bot))
                index_bot = np.where(np.logical_and(ALPHA_ANGLES == a_bot, BETA_ANGLES == b_bot))

                E_matrix[i, j], sigma_E_matrix[i, j] = compute_E(data[index, 2], data[index_bot, 2],
                                                                 data[index_a_bot, 2], data[index_b_bot, 2])

        S_strong = np.abs(-E_matrix[0, 0] + E_matrix[1, 1] + E_matrix[0, 1] + E_matrix[1, 0])
        S_weak = np.abs(E_matrix[0, 0] - E_matrix[0, 1]) + np.abs(E_matrix[1, 1] + E_matrix[1, 0])
        sigma_S = np.sqrt(np.sum(np.square(sigma_E_matrix)))

        logger.info(f'S_strong = {S_strong} ?? {sigma_S}')
        logger.info(f'S_weak = {S_weak} ?? {sigma_S}')
        angle_tuples = np.zeros(len(ALPHA_ANGLES), dtype='U40')
        for i, alpha in enumerate(ALPHA_ANGLES):
            angle_tuples[i] = f'{alpha, BETA_ANGLES[i]}'

        x_position = np.arange(0, 2 * len(ALPHA_ANGLES), 2)
        titles = ['Counter 1', 'Counter 2', 'Coincidence counts']

        for i in range(3):
            fig, ax = plt.subplots()
            fig.subplots_adjust(left=0.15, bottom=0.23)
            ax.bar(x_position, np.mean(data[:, i], axis=1))
            ax.set_xticks(x_position)
            ax.set_xticklabels(angle_tuples, rotation=45, ha='right', rotation_mode="anchor")
            ax.set_title(titles[i] +
                         f"\n CA steps = {metadata['CA_steps']}, WA steps = {metadata['WA_steps']}, " +
                         f"CB steps = {metadata['CB_steps']}, WB steps = {metadata['WB_steps']}")
            ax.set_xlabel('($\\alpha,\\beta$)')
            ax.set_ylabel('Counts')
            fig.show()
