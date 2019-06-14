# Given a Jurisdiction, preprocess the data and save it in a parquet data.

import time

import pyspark.sql.functions as f
import pyspark.sql.types as t
import sys
import unidecode
from nltk.tokenize import wordpunct_tokenize
sys.path.insert(0, '../tools/')
import tools
start_time = time.time()


# ENVIRONMENT SETTINGS

if len(sys.argv) < 2:
    print("'SLUG' and 'CAP' arguments needed.")
    exit()


slug = sys.argv[1]
cap = bool(int(sys.argv[2]))

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

all_words = tools.get_all_words(spark)
print("all_words count: ", all_words.count())

# Tokenize a text into a sequence of alphabetic and non-alphabetic characters
# Use same regexp as nltk WordPunctTokenizer().tokenize(s): \w+|[^\w\s]+


def word_tokenize(x):
    # Tokenize using NLTK wordpunct_tokenize and remove accents
    return wordpunct_tokenize(unidecode.unidecode(x.lower()))


# RDD[string] where 'string' is a single token.
ops = ops.rdd.flatMap(list).flatMap(word_tokenize).cache()

if not cap:
    print("Remove not existing words (CAP arguments '-c' is not setted)")
    all_words = sparkContext.broadcast(set(all_words.collect()))
    ops = ops.filter(lambda w: w in all_words.value)

if cap:
    cap_str = '_cap'
else:
    cap_str = '_nocap'

ops = spark.createDataFrame(ops, t.StringType())

filename = data_folder + "preprocessed/" + slug + cap_str

ops.write.mode("overwrite").text(filename, lineSep=' ')

print("Preprocessed " + slug + " completed in ",
      (time.time() - start_time), " seconds.")
