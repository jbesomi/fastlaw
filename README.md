# FASTLAW

*Fastlaw* is a law-specific word embedding model trained on a large corpus of law-related text data provided by the [Caselaw Access Project](https://case.law) (CAP). *Fastlaw* was computed using *Spark*, a distributed cluster-computing framework, and *FastText*, a library for efficient word representation learning.


The repository is composed of three main bash scripts.


- ```download_bulk_data.sh``` allows to download all jurisdiction data from the CAP website. The script accomplishes several tasks such as downloading a single file or a list of jurisdiction files, downloading all data, or downloading only public jurisdiction.

- ```wordembedding.sh``` permits to construct the word embedding. The most important parameter is the slug (*-s*) that represents the jurisdiction data based on which the word embedding will be computed.

- ```evaluation.sh``` allows to assess different models of *Fastlaw* against *FastText*. The evaluation is performed on a text classification task where the objective is to distinguish civil vs. criminal cases.


## Technical report and results
[Here](report.pdf) you can download the technical report. The aim of this document is to provide additional details about the implementation and the respective challenges encountered during development.


## Installation

The pre-processing steps that transform the initial *jsonl* file into the single tokenized *txt* file make use of *Apache PySpark* and *Apache Hadoop*. A running version of this software (preferably the latest one), is needed.

__Python dependencies__
Python 3 is required to execute the code. Moreover, extra dependencies needed can be downloaded with [pip](https://pypi.org/project/pip/):

`pip install -r requirements.txt`

__Download of bulk data__

As now, CAP has released to the public three jurisdictions:
- Arkansas, 136.7 MB (*txt*)
- Illinois, 463.0 MB (*txt*)
- New Mexico, 63.9 MB (*txt*)

To being able to download the private jurisdiction, an account on the CAP website with _unmetered access_ is needed. Once accepted, CAP will provide an API key token used to download all the jurisdiction data.

`download_bulk_data.sh` is used to download the data. It accepts the following arguments:
- `-s` (slug) download only the jurisdiction of the passed slug or list of slug
- `-a` (all) download all data

In case no parameters are given, the script download only bulk public data.

__Token.__
In order to download private jurisdiction, the following line: `token=YOUR_TOKEN` has to be added in the `config` file in the `download_bulk_data` folder

## Wordembedding

`wordembedding.sh` arguments:
- `-s` (slug) it can be a single slug or *all*. Default is *am-samoa*. If *all* is passed, the word embedding will be computed using all *jsonl* file present in the `data/bulk` folder.
- `-c` (cap) if passed, do not remove non-existing English words. When training a large dataset, it's advised to provide this argument for faster results.
- `-d` (dim) dimension of the word embedding. Default: 300.

Example: ```./wordembedding.sh -s us -c```

## Evaluation

`evaluation.sh` arguments:
- `-s` (slug) it can be a single slug or a list of slugs. The default value is a list of small jurisdiction. If multiple value are passed, each jurisdiction will be computed separately.
- `-n` (number of training cases) the number of training cases selected from a single jurisdiction. It can be a single or a list of values.

Example: ```./evaluation.sh -s "am-samoa tex" -n "100 500 100"```
