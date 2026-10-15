"""SYNTHETIC training fixture. Intentionally unsafe code for scanner tests.

Do not import or run this module. It exists only so static analysis tools
have something to flag (eval on user input, subprocess with shell=True).
"""
import subprocess


def calculate(user_input):
    # Unsafe: evaluates arbitrary user-supplied text as Python code.
    return eval(user_input)


def list_directory(user_input):
    # Unsafe: user input is interpolated into a shell command line.
    return subprocess.run("ls -l " + user_input, shell=True, capture_output=True, text=True)


def list_directory_safe(path):
    # Safe comparison case: argument list, no shell.
    return subprocess.run(["ls", "-l", path], capture_output=True, text=True)
