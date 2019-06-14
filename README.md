# FASTLAW

Fastlaw is a wordembedding model computed with [FastText](https://fasttext.cc), a library for learning of word embeddings created by Facebook's AI Research lab. The underline corpus used to produce Fastlaw is a large corpus of law data provided by the [CAP - Caselaw Access Project](https://case.law/). CAP mission is to make all U.S. case law freely accessible online.

The repo is composed of three main scripts:

- ```wordembedding.sh``` that produce a the *Fastlaw* wordembedding
- ```evaluation.sh``` that evaluate four *Fastlaw* models against *Fasttext* for a specific prediction task
- ```download_buld_data.sh``` that permits to download the CAP data


## Technical report and results
[Here](report.pdf) you can download the technical report. The aim of the document is to provide additional details about the implementation and the respective challenges encountered during development.


## Installation

The preprocessing steps that transform the initial *jsonl* file into a single tokenized *txt* file make use of Apache PySpark and Apache Hadoop. A running versions of this software (preferably the latest one), is needed.

__Python dependencies__
Python 3 is required to execute the code. Moreover, some dependencies library need to be installed
You can install all dependencies with [pip](https://pypi.org/project/pip/):

`pip install -r requirements.txt`

__Download of bulk data__

CAP has released for now to the public three jurisdiction:
- Arkansas, 136.7 MB (txt)
- Illinois, 463.0 MB (txt)
- New Mexico, 63.9 MB (txt)

To being able to download the private jurisdiction, an open account on the CAP website with _unmetered access_ is needed. Once accepted, CAP will provide an API key token that can be used to download all the jurisdiction data.

`download_bulk_data.sh` is used to download the data. It accepts the following arguments:
- `-s` (slug) download only the jurisdiction of the passed slug or list of slug
- `-a` (all) download all data

In case no parameters are given, the script download only bulk public data.
Bulk data are downloaded into the `bulk` folder on `data`.

__Token.__
In order to download private jurisdiction, the following line: `token=YOUR_TOKEN` has to be added in the `config` file in the `download_bulk_data` folder

## Wordembedding

`wordembedding.sh` arguments:
- `-s` (slug) it can be a single slug or 'all'. Default is *am-samoa*. When 'all' is passed, the word embedding will be computed using all *jsonl* file present in the `data/bulk` folder.
- `-c` (cap) if passed, do not remove non-existing english words. When training a large dataset, it's advised to provide this argument because otherwise the preprocessing steps may takes too long to complete. See the *technical report* for more details.
- `-d` (dim) dimension of the word embedding. default is 300.

## Evaluation

`evaluation.sh` arguments:
- `-s` (slug) it can be a single slug or a list of slugs. The default value is a list of small jurisdiction. If multiple value are passed, each jurisdiction will be computed separately.
- `-l` (limit) the number of cases selected from a single jurisdiction.
