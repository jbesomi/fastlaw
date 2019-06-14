#!/bin/bash

# all downloaded data will be saved into data folder as jurisdiction.jsonl

pwd
source ./config

mkdir -p ../data/bulk/
cd ../data/bulk

download() {
  # $1 : ID of Juridisction
  # $2 : Name of Jurisdiction
  id=$1
  slug=$2


  # Download the data
  curl -C - -H "Authorization: Token $TOKEN" "https://api.case.law/v1/bulk/$id/download/" \
        --output $slug.zip
  unzip -j "$slug.zip" -d $slug
  rm $slug.zip
  cd $slug
  rm *.txt

  xz -k -f --decompress *.xz
  mv -f data.jsonl ../$slug.jsonl
  cd ..
  rm -r $slug
  cd ../../
}

download $1 $2
