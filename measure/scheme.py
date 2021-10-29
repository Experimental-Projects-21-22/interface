import os
from abc import ABC, abstractmethod
from datetime import datetime
from time import sleep
from typing import Tuple, final

import numpy as np
from loguru import logger

from interface import CoincidenceCircuit, Interferometer

DATETIME_FORMAT = '%Y-%m-%d-%H:%M:%S'


class BaseScheme(ABC):
    """
    Provides a template for measurement schemes following the template method behavioural pattern. It takes care of
    setting up the serial interfaces and closing them when we are done. It furthermore takes care of saving and
    compressing data (along with metadata).
    """

    def __init__(self, coincidence_circuit: CoincidenceCircuit, interferometer: Interferometer,
                 data_shape: Tuple[int, ...], iterations: int):
        self.coincidence_circuit = coincidence_circuit
        self.interferometer = interferometer

        self.data: np.ndarray = np.zeros(data_shape)
        self.iterations = iterations

        self._timestamp: datetime = datetime.now()

    @property
    def metadata(self) -> dict:
        """
        Dictionary with metadata that is saved alongside the compressed data files. You can extend this method to add
        additional data. You should return `super().metadata.update(d)` where `d` is your dictionary.
        :return: a dictionary with metadata.
        """
        return {
            "scheme":    self.scheme_name,
            "timestamp": self.timestamp,
        }

    @property
    def scheme_name(self) -> str:
        """
        Short hand to get the name of the measurement scheme.
        """
        return self.__class__.__name__

    @property
    def timestamp(self) -> str:
        """
        Returns a formatted datetime of when the measurement scheme was run.
        """
        return self._timestamp.strftime(DATETIME_FORMAT)

    @timestamp.setter
    def timestamp(self, value: datetime):
        """
        Updates the timestamp of when the measurement started running.
        """
        self._timestamp = value

    @property
    def data_folder(self) -> str:
        """
        The folder where the data will be stored in.
        """
        return f"data/{self.scheme_name}"

    @property
    def file_name(self) -> str:
        """
        The folder the data will be stored in including the file name.
        """
        return f"{self.data_folder}/{self.timestamp}.npz"

    @final
    def __call__(self):
        """
        Runs the whole measurement scheme. It will prepare the scheme and do any required setup. It will then iterate,
        acquiring data and finally save that data. Additionally it will run the cleanup and return the acquired data.
        :return:
        """
        # Prepares the system.
        self.prepare()
        # Runs code that is required once.
        self.setup()

        # Gives the Arduinos time to get settled.
        sleep(1)
        # Run the actual measurements.
        logger.info(f"Starting measurements for {self.scheme_name}.")
        for i in range(self.iterations):
            self.iteration(i)
        logger.info(f"Finished measurements for {self.scheme_name}.")
        # Save all data.
        self.save()
        # Perform any cleanup.
        self.cleanup()
        # Return the acquired data.
        return self.data

    @final
    def prepare(self) -> None:
        """
        Prepares the system, initializes serial connections and creates the data folder if it does not exist.
        """
        logger.info(f"Preparing {self.scheme_name} measurement scheme...")
        self.timestamp = datetime.now()

        if not os.path.exists(self.data_folder):
            logger.info(f"Creating data folder: {self.data_folder}!")
            os.makedirs(self.data_folder)

        self.coincidence_circuit.__enter__()
        self.interferometer.__enter__()

    @abstractmethod
    def setup(self) -> None:
        """
        This method is run once. It should be used to set the system to a known state, par example by setting the delay
        lines to their initial values.
        """
        pass

    @abstractmethod
    def iteration(self, i: int) -> None:
        """
        This method is called repeatedly. It should be used as the main way of updating the system and then acquiring
        data from it.
        :param i: the iteration number.
        """
        pass

    @final
    def save(self) -> None:
        """
        Saves the acquired data, along with metadata, to file and compresses it.
        """
        logger.info(f"Saving data to file: {self.file_name}!")
        np.savez_compressed(self.file_name, data=self.data, **self.metadata)

    @final
    def cleanup(self) -> None:
        """
        Closes the serial connections.
        """
        logger.info(f"Tearing down {self.scheme_name} measurement scheme...")
        self.coincidence_circuit.__exit__()
        self.interferometer.__exit__()

    @staticmethod
    def analyse(data: np.ndarray) -> None:
        """
        This method can be called to analyse the acquired data. It is not run automatically. The rational for making it
        static is to signal that it is not necessarily part of the scheme and does not need to be used. It is part of
        the scheme to make it easier to swap scheme without having to think about specifying a new `analyse` method
        somehow. Additionally, since it is static it can be called without creating an object thus allowing it to be run
        without needing to instantiate serial connections.
        :param data: the data as acquired by running the scheme.
        """
        pass
