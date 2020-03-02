"""Helper for regenerating test models from schemas."""
import os
import subprocess
import sys


SCHEMA_DIR = "tests/jsonschemas"
OUTPUT_DIR = "tests/models"


def _generate():
    for filename in os.listdir(SCHEMA_DIR):
        path = os.path.join(SCHEMA_DIR, filename)
        if not os.path.isfile(path):
            continue
        sys.stdout.write("*")
        subprocess.check_call(
            ["python", "statham", "--input", path, "--output", OUTPUT_DIR]
        )


if __name__ == "__main__":
    _generate()
