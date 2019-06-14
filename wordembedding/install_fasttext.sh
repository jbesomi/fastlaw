#!/bin/bash

# Check if fastText exist
fasttext_folder=$1
if [ ! -d "$fasttext_folder" ]
then
      echo "Installing FastText ..."
      wget https://github.com/facebookresearch/fastText/archive/v0.1.0.zip
      unzip v0.1.0.zip
      rm v0.1.0.zip
      mv fastText-0.1.0 $fasttext_folder
      cd $fasttext_folder
      make
fi

mkdir -p ../data/wordembedding/
mkdir -p ../data/$fasttext_folder
