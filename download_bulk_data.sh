#!/bin/bash

source download_bulk_data/config # if exist, load TOKEN data

# SLUG OF PUBLIC :: ark ill nm

cd download_bulk_data

# parse arguments
while getopts ":s:a" opt; do
      case $opt in
            # slug
            s) SLUG="$OPTARG" ;;

            # download all data
            a) ALL="$OPTARG" ;;

            \?) echo "Invalid option provided -$OPTARG" >&2
                  ;;
      esac
done


# If no parameters, download public.

if [ "$#" == 0 ]; then
    python3 download_bulk_data.py public
    exit
fi


# if token is empty, download public
if [ -z "$TOKEN" ]
then
      # if slug is defined and slug is equal to one of the three possible, download it
      if [ ! -z ${SLUG+x} ];
      then
            for slug in $SLUG
            do
                  python3 download_bulk_data.py $slug
            done
            exit
      else
            echo "Download all public jurisdictions."
            exit
      fi

fi


if [ ! -z ${ALL+x}  ]
then
      echo "Download all jurisdictions (bash)."
      python3 download_bulk_data.py all $TOKEN
      exit
fi

if [ ! -z ${SLUG+x}  ]
then
      for slug in $SLUG
      do
            python3 download_bulk_data.py $slug $TOKEN

      done
      exit
fi
