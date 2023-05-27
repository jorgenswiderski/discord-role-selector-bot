#!/bin/sh -x

# Activate Python virtual environment
source env/bin/activate

# Upgrade dependencies
python3.11 -m pip install --upgrade pip

if [ -f requirements.txt ]; then
    pip install -r requirements.txt;
fi
