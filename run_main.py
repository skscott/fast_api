#!/home/ss/Source/fast_api/bin/python
# run_main.py
# Run
# source ~//home/ss/Source/fast_api/.venv/bin/activate
# python3 /home/ss//home/ss/Source/fast_api/run_dev.py

import sys
import os
import subprocess

# Absolute path to your project root
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Set PYTHONPATH to the project root so 'hive_api' is importable
os.environ["PYTHONPATH"] = PROJECT_ROOT

# Command to run your main app using module-style
cmd = [sys.executable, "-m", "fast_api.app.main"]

import uvicorn

if __name__ == "__main__":
    uvicorn.run("fast_api.app.main:app", host="127.0.0.1", port=8800, reload=True)

