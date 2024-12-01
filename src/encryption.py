import os

def generate_key(key_length):
    return os.urandom(key_length)


