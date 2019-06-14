#!/bin/sh

SLUG="us"
DIM="300"

mkdir -p "../data/downloaded/wordembedding/"

gcloud compute scp --recurse jonathanbesomi@caselaw-instance-1:/home/jonathanbesomi/fastlaw-temp/data/wordembedding/fastlaw_${SLUG}_${DIM}.vec ../data/downloaded/wordembedding/fastlaw_${SLUG}_${DIM}.vec
