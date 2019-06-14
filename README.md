# FASTLAW

Fastlaw is a wordembedding model computed with [FastText](https://fasttext.cc), a library for learning of word embeddings created by Facebook's AI Research lab. The underline corpus used to produce Fastlaw is a large corpus of law data provided by the [CAP - Caselaw Access Project](https://case.law/). CAP mission is to make all U.S. case law freely accessible online.

There are two main scripts:

- ```wordembedding.sh``` that produce a the *Fastlaw* wordembedding
- ```evaluation.sh``` that evaluate *Fastlaw* models against *Fasttext* for a specific prediction task

## Technical report and results



## Installation

The preprocessing steps that transform the initial JSON file into a single tokenized TXT file make use of Apache PySpark and Apache Hadoop. A running versions of this software (preferably the latest one), are therefore needed.

__Apache Spark and Hadoop__



__Python dependencies__
Python 3 is required to execute the code. Moreover, some dependencies library need to be installed
You can install all dependencies with [pip](https://pypi.org/project/pip/):

`pip install -r requirements.txt`

__Download of bulk data__

CAP has released for now to the public three jurisdiction:
- Arkansas, 136.7 MB (txt)
- Illinois, 463.0 MB (txt)
- New Mexico, 63.9 MB (txt)

To being able to download the private jurisdiction, an open account on the CAP website with _unmetered access_ is needed. Once accepted, CAP will provide an API key token that can be used to download all jurisdiction data.

`download_bulk_data.sh` is an utility file to download the data.
It has the following arguments:
- `-t` (token) CAP api key
- `-s` (slug) download only the jurisdiction of the passed slug or list of slug
- `-a` (all) download all data

In case no parameters are given, the script download only bulk public data.
Bulk data are downloaded into the `bulk` folder on `data`.

__Token.__ To avoid always passing the `t` (token) parameters, a `config` file can be added into the `download_bulk_data` folder with the following line: `token=YOUR_TOKEN`.

## Download of Fastlaw

We provide two Fastlaw Wordembedding model that can be used as a valid substitute to a more generic wordembedding model such as Fasttext or Glove for law-related NLP-tasks such has predictions or text classification.

### fastlaw_cap.vec
__Overview__

      Size 300 MB:
      Number of words:
      Word embedding dimension:  
      FastText parameters:
      Download link:
      Jurisdiction: all

*fastlaw_cap.vec* has been trained on the whole CAP dataframe and does contains CAP specific words such has personal name of attorneys and other CAP-related words.

**This model may be used** for NLP tasks when dealing with law documents that **does** come from the CAP dataset such has the prediction task used in this repository (see the *evaluation* section).

The preprocessing steps of removing accents, cleaning some words such has *hello5* to *hello* is performed on the data.

### fastlaw.vec
__Overview__

      Size 300 MB:
      Number of words:
      Word embedding dimension:  
      FastText parameters:
      Download link:
      Jurisdiction: U.S

fastlaw.vec **contains only words existing in the English vocabulary**. Personal name, grammar mistakes and other non-existing words have been removed before computing the wordembedding. It has been trained only with the U.S jurisdiction JSON file.

**This model may be used** for NLP tasks when dealing with law documents that **does not** come from the CAP dataset.

The preprocessing steps of removing accents, cleaning some words such has *hello5* to *hello* is performed on the data.


## Wordembedding

As already mentioned, CAP data contains many misspelled words and grammar mistakes since they have been digitalised by an optical character recogniser.

For that reason, some preprocessing steps are needed to improve the quality of the final wordembedding model. For more information, refer to the *technical report*.


`wordembedding.sh` arguments:
- `-s` (slug) it can be a single slug or 'all'. Default 'am-samoa'. When 'all' is passed, the woremedding will be computed starting from all jsonl data present in the `data/bulk` folder.
- `-c` (cap) if passed, do not remove non-existing english words. When training a large dataset, it's advised to provide this argument because otherwise the preprocessing steps may takes too long to complete. See the *technical report* for more details.
- `-d` (dim) dimension of the word embedding. default is 300.

## Evaluation

This sections aim is to evaluate the two models (**fastlaw** and **fastlaw_cap**) against FastText and against a random initialisation on a classification task.

The classification task consist of detect weather a law case is *civil* or *criminal*.

A simple fast-forwarding model with a word embedding layer is used.

### Context and results
Using a specialised word embedding is worthwhile when the training dataset is small. Otherwise, when enough data are available, the NN is able to update the wordembedding, making a specifc word embedding almost worthwhile.

Therefore, what it matters to assess the quality of Fastlaw is how well does it behave in case of a limited number of training tuples. On a more large dataset, instead, we should expect that the convergence to the optimal solutions should happen quickly with a specific word embedding.

To check the results of the evaluation, please refer to the *technical report and results*


`evaluation.sh` arguments:
- `-s` (slug) it can be a single slug or a list of slugs. The default value is a list of small jurisdiction. If multiple value are passed, each jurisdiction will be computed separately.

- `-l` (limit) the number of cases selected from a single jurisdiction. The default values are [100, 500, 1000, 2000, 5000, 7000, 10000].
