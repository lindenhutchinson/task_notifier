
from tools.ontrack_ctrl import OntrackCtrl
import os
from tools.utils import ensure_directory_exists, write_to_file
from find_ontrack_updates import load_token
import sys

def write_tasks_to_pdf(ctrl, directory="units"):
    directory = ensure_directory_exists(directory)
    unit_tasks = ctrl.get_unit_tasks_pdf()
    for unit, tasks in unit_tasks.items():
        unit_dir = ensure_directory_exists(f"{directory}/{unit}")
        for task in tasks:
            write_to_file(task['content'], f"{unit_dir}/{task['name']}.pdf", write_mode="wb")

if __name__ == "__main__":
    if not os.getenv('USER'):
        print("Run generate_env_file.py first")
        sys.exit()

    # requires .env file created by running generate_env_file.py
    token = load_token()
    ontrack = OntrackCtrl(os.getenv('USER'), token)
    write_tasks_to_pdf(ontrack)