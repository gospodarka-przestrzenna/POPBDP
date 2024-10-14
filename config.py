import os

DB_FILENAME = "data.gpkg"

current_dir = os.path.dirname(os.path.realpath(__file__))
DB_PATH = os.path.join(current_dir,DB_FILENAME)