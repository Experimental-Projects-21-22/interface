import re
from typing import List

DELAY_LINES: List[str] = ['CA', 'WA', 'CB', 'WB']
DELAY_STEP_SIZE: float = 0.25
DELAY_STEPS: int = 2 ** 8 - 1
DELAY_REGEX = re.compile(r'(\d+)')
