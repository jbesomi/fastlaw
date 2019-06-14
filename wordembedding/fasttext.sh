#!/bin/bash

# default values
SLUG=${1:-"am-samoa"}
DIM=${2:-"300"}
CAP=${3:-"nocap"}


fasttext_folder=fasttext

./install_fasttext.sh $fasttext_folder

wait

# compute wordEmbedding
./$fasttext_folder/fasttext skipgram -thread 32 -minn 0 -maxn 0 -dim $DIM -minCount 20 -input ../data/preprocessed/wordembedding_${SLUG}_${CAP}.txt -output "../data/wordembedding/fastlaw_${DIM}_${SLUG}_${CAP}"
