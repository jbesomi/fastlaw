#!/bin/bash

set -e


DIM=300

# parse arguments
while getopts ":s:cd:" opt; do
      case $opt in
            # slug
            s) SLUG="$OPTARG" ;;

            # cap
            c) CAP="$OPTARG" ;;

            # dimension
            d) DIM="$OPTARG" ;;

            \?) echo "Invalid option provided -$OPTARG" >&2
                  ;;
      esac
done

# if empty, set default
if [ -z "$SLUG" ]
then
      SLUG='am-samoa'
fi

# if CAP is set:
if [ ! -z ${CAP+x} ]
then
      CAP=1
      CAP_STR='cap'
else
      CAP=0
      CAP_STR='nocap'
fi

cd wordembedding

echo "Preprocessing the data for jurisdiction '$SLUG'"
python3 preprocess.py $SLUG $CAP

wait

echo "Merge all txt file into a single one ..."
./merge.sh $SLUG $CAP_STR

wait

echo "Compute wordembedding ..."
./fasttext.sh $SLUG $DIM $CAP_STR
