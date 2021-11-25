from os.path import abspath, dirname, join

# Directory to store data in.
DATA_DIRECTORY = abspath(join(dirname(__file__), '../data'))
# Datetime format for filenames.
DATETIME_FORMAT = '%Y-%m-%d-%H:%M:%S'
