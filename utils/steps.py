"""
Written by:
    Julian van Doorn <j.c.b.van.doorn@umail.leidenuniv.nl>
"""

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
        if np.any(steps < -128) or np.any(steps > 127):
            raise ValueError("Steps must be in the range [-128, 127].")
    else:
        steps = int(steps)
        if steps < -128 or steps > 127:
            raise ValueError("Steps must be in the range [-128, 127].")

    return steps
