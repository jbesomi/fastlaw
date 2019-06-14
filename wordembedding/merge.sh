#!/bin/sh

SLUG=${1:-"am-samoa"}
CAP=${1:-"cap"}

hadoop fs -cat "../data/preprocessed/${SLUG}_${CAP}/part*" | hadoop fs -put -f - ../data/preprocessed/wordembedding_${SLUG}_${CAP}.txt
