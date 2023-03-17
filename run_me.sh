#!/bin/bash
# Launch the script from the project root folder.
. venv/bin/activate && cd manufacturing_model && python running_model.py && python merge_logs.py
cd ../causal_model && python -m notebook