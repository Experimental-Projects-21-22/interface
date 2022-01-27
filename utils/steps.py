from typing import overload

import numpy as np


@overload
def validate_interferometer_steps(steps: np.ndarray) -> np.ndarray:
    ...


@overload
def validate_interferometer_steps(steps: int) -> int:
    ...


def validate_interferometer_steps(steps):
    """
    Raises a ValueError if the amount of steps is not in the range [-128, 127]. Else it returns steps.
    """
    if isinstance(steps, np.ndarray):
        steps = steps.astype(int)
    else:
        steps = int(steps)

    return steps
