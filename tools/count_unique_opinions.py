# Given a Jurisdiction, preprocess the data and save it in a parquet data.

import time

import pyspark.sql.functions as f
import sys
import unidecode
from nltk.tokenize import wordpunct_tokenize
import tools
start_time = time.time()

slug = sys.argv[1]

data_folder = '../data/'

spark = tools.get_spark()
sparkContext = spark.sparkContext

data = tools.get_data(spark, slug)
ops = tools.get_opinions(spark, data)


# Transform 'word5' into 'word'
ops = ops.withColumn(
    "text",
    f.regexp_replace("text", "(\d+|\D+)", " $1")
)

# Transforms word 'the_' into 'the'
ops = ops.withColumn(
    "text",
    f.regexp_replace("text", "(\w+[^\\w{_}]|\w+)", " $1")
)

# Replace numbers with at least 2 digits with 'number'
ops = ops.withColumn(
    "text",
    f.regexp_replace("text", "\d{2,}", " number ")
)

# Tokenize a text into a sequence of alphabetic and non-alphabetic characters
# Use same regexp as nltk WordPunctTokenizer().tokenize(s): \w+|[^\w\s]+


def word_tokenize(x):
    # Tokenize using NLTK wordpunct_tokenize and remove accents
    return wordpunct_tokenize(unidecode.unidecode(x.lower()))


# RDD[string] where 'string' is a single token.
unique_tokens = ops.rdd.flatMap(list).flatMap(word_tokenize).count()


print(slug, "has ", unique_tokens, "tokens on opinions.")
