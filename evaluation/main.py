import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.model_selection import train_test_split
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import embedding_matrix as em
import plot
import ml
import sys
import pyspark.sql.types as t
import pyspark.sql.functions as f
import warnings
import time
import os
warnings.simplefilter(action='ignore', category=FutureWarning)


sns.set()

sys.path.insert(0, '../tools/')
import tools

mpl.rcParams['savefig.dpi'] = 300  # Save pictures in HD

if len(sys.argv) < 3:
    print("Both slug and limit arguments needed.")
    exit()

slug = sys.argv[1]
num_train_cases = sys.argv[2].split()
num_train_cases = list(map(int, num_train_cases))

# PARAMETER SETTINGS
epochs = 50
batch_size = 20

# for tokenizer the maximum number of words to keep,
# based on word frequency. Only the most common num_words-1
# words will be kept
num_words = 50000

maxlen = 100  # number of dimension of each train sample

max_words_by_case = 1500

verbose = False

max_num_cases = 10000

# log for execution time
log_time = time.strftime("%d%m_%H%M", time.localtime())

# random seed, None=Random, int=selected
random_seed = None


def stats_sentences_length(data):
    # COUNT LARGEST SENTENCE ...add_months
    count = data.rdd.map(lambda row: len(row['text'].split(' ')))
    # TODO: update Spark and Use NumericType()
    count = spark.createDataFrame(count, t.StringType()).toPandas()
    count.value = count.value.astype(int)
    max_num_words = count.value.max()

    print("\nStatistics about the length of words in the corpus: ")
    print(count.value.describe())
    print("Largest case sentence has ", max_num_words, " number of words.\n")
    count.value.plot.hist()
    plt.savefig('plot/distribution_number_of_words.png')
# stats_sentences_length(data)


def save_first_case(data):
    print("save first case... ")
    first = pd.DataFrame(data.first())
    first.to_csv("first_case.csv")
# save_first_case(data)


def evaluate(box, num_train_cases, spark, slug, results_table):

    data = tools.get_data(spark, slug)
    data = tools.get_opinions(spark, data).persist()

    print(slug + " has ", data.count(), "different cases")

    # Compute target values:
    target_true = ['State', 'state', 'Commonwealth', 'commonwealth']

    contains_keywords = data.name_abbreviation.contains(target_true[0])
    for k in target_true[1:]:
        contains_keywords = contains_keywords | data.name_abbreviation.contains(
            k)
    data = data.withColumn("target", contains_keywords)


    # compute sample size to be close to
    total_size = data.count()
    frac = (max_num_cases / total_size)

    print("Limit the data to 10'000 cases.")
    #data = data.sample(False, frac, 42).persist()

    # preprocess
    # Transform 'word5' into 'word'
    data = data.withColumn(
        "text",
        f.regexp_replace("text", "(\d+|\D+)", " $1")
    )

    # Transforms word 'the_' into 'the'
    data = data.withColumn(
        "text",
        f.regexp_replace("text", "(\w+[^\\w{_}]|\w+)", " $1")
    )

    #print(slug + " has ", data.count(), "different cases")

    # remove target words from text
    regex_rules = '(' + '|'.join(target_true) + ')'
    data = data.withColumn(
        'text', f.regexp_replace('text', regex_rules, ' '))

    def limit_number_of_words(data):
        # limit number of words
        print("Limiting the number of words for each case to:", max_words_by_case)
        schema = data.schema
        data = data.rdd.map(lambda row: (' '.join(row['text'].split()[:max_words_by_case]),
                                         row['name_abbreviation'],
                                         row['target']))
        data = spark.createDataFrame(data, schema)

        return data

    data = limit_number_of_words(data)

    data = data.toPandas()

    data['target'] = data['target'] * 1

    print(data[data['target'] == 0])

    # rebalance the data
    data = ml.rebalance(data, random_seed)
    print("distribution of target value after balancing:\n",
          data.target.value_counts())

    # preprocess
    text = data['text'].values
    y = data['target'].values

    text_train, text_test, y_train, y_test = train_test_split(
        text, y, train_size=num_train_cases, random_state=1000)

    tokenizer = Tokenizer(num_words)
    tokenizer.fit_on_texts(text_train)

    # add 1 because of reserved 0 index
    vocab_size = len(tokenizer.word_index) + 1

    table_temp = pd.Series()
    table_temp['slug'] = slug
    table_temp['num_train_cases'] = num_train_cases
    table_temp['log_time'] = log_time

    # used for information of the plot
    num_ones_train = (y_train == 1).sum()
    #num_ones_test = (y_test == 1).sum()

    print("On train, there are ", num_ones_train, "target value to 1.")

    table_temp['maxlen'] = maxlen
    table_temp['max_words_by_case'] = max_words_by_case

    X_train = tokenizer.texts_to_sequences(text_train)
    X_test = tokenizer.texts_to_sequences(text_test)

    X_train = pad_sequences(X_train, padding='post', maxlen=maxlen)
    X_test = pad_sequences(X_test, padding='post', maxlen=maxlen)

    # Create validation
    X_test, X_val, y_test, y_val = train_test_split(
        X_test, y_test, test_size=int(num_train_cases * 2), random_state=random_seed)  # here test is validation

    print("X_train size: ", X_train.shape[0])
    print("X_test size: ", X_test.shape[0])
    print("X_val size: ", X_val.shape[0])

    table_temp['train_size'] = X_train.shape[0]
    table_temp['test_size'] = X_test.shape[0]
    table_temp['val_size'] = X_val.shape[0]

    # ML, prediction

    table_temp['box'] = box
    if box == 4:
        box = ml.black_box_4
    elif box == 3:
        box = ml.black_box_3
    elif box == 2:
        box = ml.black_box_2
    else:
        box = ml.black_box

    # 1. Random wordembedding initialization
    print("Random wordembedding initialization.")
    model_random = box(vocab_size, embedding_dim=300,
                       embedding_matrix=None, maxlen=maxlen)
    history_random = model_random.fit(X_train, y_train,
                                      epochs=epochs,
                                      verbose=verbose,
                                      validation_data=(
                                          X_val, y_val),
                                      batch_size=batch_size)

    print(model_random.summary())

    table_temp = ml.accuracy(model_random, history_random, X_train,
                             y_train, X_test, y_test, table_temp, 'model_random')

    # 2. fastlaw_cap_ngram
    embedding_matrix_fastlaw_cap_ngram = em.loadEmbeddingMatrix(
        'fastlaw_cap_ngram', tokenizer)

    print("fastlaw_cap_ngram:")
    model_fastlaw_cap_ngram = box(vocab_size,
                                  embedding_dim=300,
                                  embedding_matrix=embedding_matrix_fastlaw_cap_ngram,
                                  maxlen=maxlen)

    history_fastlaw_cap_ngram = model_fastlaw_cap_ngram.fit(X_train, y_train,
                                                            epochs=epochs,
                                                            verbose=verbose,
                                                            validation_data=(
                                                                X_val, y_val),
                                                            batch_size=batch_size)

    table_temp = ml.accuracy(model_fastlaw_cap_ngram, history_fastlaw_cap_ngram,
                             X_train, y_train, X_test, y_test, table_temp, 'fastlaw_cap_ngram')
    # 3. fastlaw_cap_zero
    embedding_matrix_fastlaw_cap_zero = em.loadEmbeddingMatrix(
        'fastlaw_cap_zero', tokenizer)

    print("fastlaw_cap_zero:")
    model_fastlaw_cap_zero = box(vocab_size,
                                 embedding_dim=300,
                                 embedding_matrix=embedding_matrix_fastlaw_cap_zero,
                                 maxlen=maxlen)

    history_fastlaw_cap_zero = model_fastlaw_cap_zero.fit(X_train, y_train,
                                                          epochs=epochs,
                                                          verbose=verbose,
                                                          validation_data=(
                                                              X_val, y_val),
                                                          batch_size=batch_size)

    table_temp = ml.accuracy(model_fastlaw_cap_zero, history_fastlaw_cap_zero,
                             X_train, y_train, X_test, y_test, table_temp, 'fastlaw_cap_zero')

    # 4. fastlaw_nocap_ngram
    embedding_matrix_fastlaw_nocap_ngram = em.loadEmbeddingMatrix(
        'fastlaw_nocap_ngram', tokenizer)

    print("fastlaw_nocap_ngram:")
    model_fastlaw_nocap_ngram = box(vocab_size,
                                    embedding_dim=300,
                                    embedding_matrix=embedding_matrix_fastlaw_nocap_ngram,
                                    maxlen=maxlen)

    history_fastlaw_nocap_ngram = model_fastlaw_nocap_ngram.fit(X_train, y_train,
                                                                epochs=epochs,
                                                                verbose=verbose,
                                                                validation_data=(
                                                                    X_val, y_val),
                                                                batch_size=batch_size)

    table_temp = ml.accuracy(model_fastlaw_nocap_ngram, history_fastlaw_nocap_ngram,
                             X_train, y_train, X_test, y_test, table_temp, 'fastlaw_nocap_ngram')

    # 5. fastlaw_nocap_zero
    embedding_matrix_fastlaw_nocap_zero = em.loadEmbeddingMatrix(
        'fastlaw_nocap_zero', tokenizer)

    print("fastlaw_nocap_zero:")
    model_fastlaw_nocap_zero = box(vocab_size,
                                   embedding_dim=300,
                                   embedding_matrix=embedding_matrix_fastlaw_nocap_zero,
                                   maxlen=maxlen)

    history_fastlaw_nocap_zero = model_fastlaw_nocap_zero.fit(X_train, y_train,
                                                              epochs=epochs,
                                                              verbose=verbose,
                                                              validation_data=(
                                                                  X_val, y_val),
                                                              batch_size=batch_size)

    table_temp = ml.accuracy(model_fastlaw_nocap_zero, history_fastlaw_nocap_zero,
                             X_train, y_train, X_test, y_test, table_temp, 'fastlaw_nocap_zero')

    # 6. Fasttext
    embedding_matrix_fasttext = em.loadEmbeddingMatrix(
        'fastlaw_nocap_zero', tokenizer)

    print("fasttext:")
    model_fasttext = box(vocab_size,
                         embedding_dim=300,
                         embedding_matrix=embedding_matrix_fasttext,
                         maxlen=maxlen)

    history_fasttext = model_fasttext.fit(X_train, y_train,
                                          epochs=epochs,
                                          verbose=verbose,
                                          validation_data=(
                                              X_val, y_val),
                                          batch_size=batch_size)

    table_temp = ml.accuracy(model_fasttext, history_fasttext,
                             X_train, y_train, X_test, y_test, table_temp, 'fasttext')

    # SAVE OUTPUT.

    plot.save_loss(history_random, history_fasttext,
                   history_fastlaw_cap_zero, num_train_cases, slug, log_time)

    plot.save_acc(history_random, history_fasttext,
                  history_fastlaw_cap_zero, num_train_cases, slug, log_time)

    plot.save_val_acc(history_random, history_fasttext,
                      history_fastlaw_cap_zero, num_train_cases, slug, log_time)

    results_table = results_table.append(table_temp, ignore_index=True)
    return results_table


eval_file = "results/" + slug + "/evaluation.csv"

if os.stat(eval_file).st_size == 0:  # file is empty
    results_table = pd.DataFrame()
else:
    results_table = pd.read_csv(eval_file)

spark = tools.get_spark()

for box in [4]:
    for ntc in num_train_cases:
        results_table = evaluate(box, ntc, spark, slug, results_table)
        results_table.to_csv(eval_file, index=False)  # for backup
