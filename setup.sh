#!/bin/bash

# Initialize the submodules.
git submodule update --init --recursive

# Execute the script
python MyScript.py $1 > $2

# Open the output file using default application.
if [ "$(uname)" == "Darwin" ]; then
    # OSx:
    open $2
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # Linux:
    xdg-open $2
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ]; then
    # If windows:
    start $2
elif [[ $(uname -s) == CYGWIN* ]]; then
    # cygwin:
    cygstart $2
fi



