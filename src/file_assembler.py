import hashlib
import os


def assemble_file(chunks, output_path):
    with open(output_path, "wb") as f:
        for chunk in chunks:
            f.write(chunk)


