import os
from abc import ABC, abstractmethod
from datetime import datetime
from time import sleep
from typing import Tuple, final

import numpy as np
from loguru import logger

from interface import CoincidenceCircuit, Interferometer

DATETIME_FORMAT = '%Y-%m-%d-%H:%M:%S'


class Scheme(ABC):
    def __init__(self, coincidence_circuit: CoincidenceCircuit, interferometer: Interferometer,
                 data_shape: Tuple[int, ...], iterations: int):
        self.coincidence_circuit = coincidence_circuit
        self.interferometer = interferometer

        self.data: np.ndarray = np.zeros(data_shape)
        self.iterations = iterations

        self._timestamp: datetime = datetime.now()

    @property
    def metadata(self) -> dict:
        return {
            "scheme":    self.scheme_name,
            "timestamp": self.timestamp,
        }

    @property
    def scheme_name(self) -> str:
        return self.__class__.__name__

    @property
    def timestamp(self) -> str:
        return self._timestamp.strftime(DATETIME_FORMAT)

    @timestamp.setter
    def timestamp(self, value: datetime):
        self._timestamp = value

    @property
    def data_folder(self) -> str:
        return f"data/{self.scheme_name}"

    @property
    def file_name(self) -> str:
        return f"{self.data_folder}/{self.timestamp}.npz"

    @final
    def run(self) -> np.ndarray:
        # Prepares the system.
        self.prepare()
        # Runs code that is required once.
        self.setup()

        # Gives the Arduinos time to get settled.
        sleep(1)
        # Run the actual measurements.
        for i in range(self.iterations):
            self.iteration(i)

        # Save all data.
        self.save()
        # Perform any cleanup.
        self.teardown()
        # Return the acquired data.
        return self.data

    @final
    def prepare(self):
        logger.info(f"Preparing {self.scheme_name} measurement scheme...")
        self.timestamp = datetime.now()

        if not os.path.exists(self.data_folder):
            logger.info(f"Creating data folder: {self.data_folder}!")
            os.makedirs(self.data_folder)

        self.coincidence_circuit.__enter__()
        self.interferometer.__enter__()

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def iteration(self, i):
        pass

    @final
    def save(self):
        logger.info(f"Saving data to file: {self.file_name}!")
        np.savez_compressed(self.file_name, data=self.data, **self.metadata)

    @final
    def teardown(self):
        logger.info(f"Tearing down {self.scheme_name} measurement scheme...")
        self.coincidence_circuit.__exit__()
        self.interferometer.__exit__()
