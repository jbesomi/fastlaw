#!/bin/bash

# Evaluation

SLUG="am-samoa alaska dakota-territory vt nh sd vt wyo"
NUM_TRAIN_CASES="100 200 300 400 500 5000" # maximum number of trained cases

# parse arguments
while getopts ":s:n:" opt; do
  case $opt in

    s) SLUG="$OPTARG";;

    l) NUM_TRAIN_CASES="$OPTARG";;

    \?) echo "Invalid option provided -$OPTARG" >&2
    ;;
  esac
done

for s in $SLUG
do
      mkdir -p "evaluation/results/$s"
      ./download_bulk_data.sh -s $s
done

cd evaluation
python3 main.py "$SLUG" "$NUM_TRAIN_CASES"
