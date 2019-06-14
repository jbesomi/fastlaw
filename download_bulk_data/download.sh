#!/bin/sh

# PARAMETERS $1 = 'mock' or 'ny', or 'all',
# PARAMETERS $2 = 'skip' or 'no-skip', if not passed the default is 'skip'

# give access to all files
chmod +x *.sh

if [ -z "$2" ]
then
      param_skip="skip" # default
else
      param_skip=$2
fi

python3 download_bulk_data.py $1 $param_skip
#python merge_bulk_data.py
