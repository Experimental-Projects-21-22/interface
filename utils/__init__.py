from os.path import abspath, dirname, join

# Maximum number of steps for a delay line.
DELAY_STEPS: int = 2 ** 8 - 1
# File containing the calibration data.
DELAY_LINE_CALIBRATION_FILE = abspath(join(dirname(__file__), '../data/calibration/delay_lines.csv'))
