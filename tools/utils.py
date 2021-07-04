import os

def ensure_directory_exists(dir):
    try:
        os.mkdir(dir)
        return dir
    except OSError as e:
        return dir

def write_to_file(content, filename, write_mode="w"):
    with open(filename, write_mode) as fn:
        fn.write(content)

def load_from_file(filename):
    try:
        with open(filename, "r") as fn:
            return fn.read()
    except FileNotFoundError:
        return None
