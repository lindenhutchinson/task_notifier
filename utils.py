import os

def ensure_directory_exists(dir):
    try:
        os.mkdir(dir)
        return dir
    except OSError as e:
        return dir

def write_to_file(content, filename):
    with open(filename, "w") as fn:
        fn.write(content)


def load_from_file(filename):
    try:
        with open(filename, "r") as fn:
            return fn.read()
    except FileNotFoundError:
        return None
