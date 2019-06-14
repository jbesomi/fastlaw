# LOAD DATA, given the slug of the json file, load the data
import glob
from pyspark.sql.functions import explode
from pyspark.sql import SparkSession
from sys import platform
from string import punctuation


def get_spark():
    if platform == "linux" or platform == "linux2":
        print("This is a linux platform.")
        spark = (
            SparkSession.builder.appName("preprocess")
            .master("local[*]")
            .config("spark.driver.memory", "60g")
            .config("spark.executor.memory", "30g")
            .config("spark.driver.maxResultSize", "4g")
            .getOrCreate()
        )
    else:
        print("This is not a linux platform.")
        spark = (
            SparkSession.builder.appName("preprocess")
            .master("local[*]")  # take all available cores
            .config("spark.driver.memory", "14g")
            .config("spark.executor.memory", "14g")
            .getOrCreate()
        )
    return spark


def get_data(spark, slug):

    if slug == 'all':
        list_jsonl = glob.glob("../data/bulk/*.jsonl")
    else:
        print("Load data of ", slug)
        list_jsonl = glob.glob("../data/bulk/" + slug + ".jsonl")
    print("Loaded jurisdiction: ", list_jsonl)
    data = None
    if list_jsonl is not None:
        data = spark.read.json(list_jsonl)
    return data


def get_opinions(spark, data):
    data.createOrReplaceTempView("data")

    # Tranfsorm nested casebody.data.opinions into single row of text
    opinions = spark.sql(
        "SELECT casebody.data.opinions, name_abbreviation FROM data")

    opinions = opinions.select(
        explode("opinions").alias("elements"), "name_abbreviation")
    opinions = opinions.select("elements.*",  'name_abbreviation')

    # filter not null element
    opinions = opinions.filter("text is not null")

    return opinions.select('text', 'name_abbreviation')


def get_number_partitions():
    if platform == "linux" or platform == "linux2":
        return 64
    else:
        return 8


def get_all_words(spark):

    all_words_file = "all_words.txt"

    sparkContext = spark.sparkContext
    all_words = sparkContext.textFile(all_words_file)
    all_words = all_words.map(lambda w: w.lower()).distinct().persist().cache()

    # add 'punctuation'
    rdd_punctuation = sparkContext.parallelize(set(punctuation))
    all_words = all_words.union(rdd_punctuation)

    return all_words
