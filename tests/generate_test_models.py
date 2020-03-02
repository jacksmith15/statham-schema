"""Helper for regenerating test models from schemas."""
import os
import subprocess
import sys


SCHEMA_DIR = "tests/jsonschemas"
OUTPUT_DIR = "tests/models"


def _generate():
    for idx, filename in enumerate(os.listdir(SCHEMA_DIR)):
        sys.stdout.write("*")
        subprocess.call(
            [
                "python",
                "statham",
                "--input",
                f"{SCHEMA_DIR}/{filename}",
                "--output",
                OUTPUT_DIR,
            ]
        )


if __name__ == "__main__":
    _generate()
