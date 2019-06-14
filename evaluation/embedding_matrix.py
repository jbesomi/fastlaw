import gc
import numpy as np
import sys


def loadEmbeddingMatrix(typeToLoad, tokenizer):
    # load different embedding file from Kaggle depending on which embedding
    # matrix we are going to experiment with

    embed_size = 300

    if(typeToLoad == "fastlaw_cap_ngram"):
            EMBEDDING_FILE = '../data/wordembedding/fastlaw_300_us_cap_ngram.vec'
    if(typeToLoad == "fastlaw_cap_zero"):
            EMBEDDING_FILE = '../data/wordembedding/fastlaw_300_us_cap_zero.vec'
    if(typeToLoad == "fastlaw_nocap_ngram"):
            EMBEDDING_FILE = '../data/wordembedding/fastlaw_300_us_nocap_ngram.vec'
    if(typeToLoad == "fastlaw_nocap_zero"):
            EMBEDDING_FILE = '../data/wordembedding/fastlaw_300_us_nocap_zero.vec'
    elif(typeToLoad == "fasttext"):
        EMBEDDING_FILE = '../data/wordembedding/fasttext.vec'
        embed_size = 300

    embeddings_index = dict()
    # Transfer the embedding weights into a dictionary by iterating through every line of the file.
    f = open(EMBEDDING_FILE)
    next(f)
    for line in f:
        # split up line into an indexed array
        values = line.split()
        # first index is word
        word = values[0]
        # store the rest of the values in the array as a new array
        coefs = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = coefs  # 50 dimensions
    f.close()

    print('Loaded %s word vectors.' % len(embeddings_index))

    gc.collect()
    # We get the mean and standard deviation of the embedding weights so that we could maintain the
    # same statistics for the rest of our own random generated weights.
    all_embs = np.stack(list(embeddings_index.values()))
    emb_mean, emb_std = all_embs.mean(), all_embs.std()

    nb_words = len(tokenizer.word_index) + 1
    # We are going to set the embedding size to the pretrained dimension as we are replicating it.
    # the size will be Number of Words in Vocab X Embedding Size
    embedding_matrix = np.random.normal(
        emb_mean, emb_std, (nb_words, embed_size))
    gc.collect()

    # With the newly created embedding matrix, we'll fill it up with the words that we have in both
    # our own dictionary and loaded pretrained embedding.
    embeddedCount = 0
    for word, i in tokenizer.word_index.items():
        # then we see if this word is in glove's dictionary, if yes, get the corresponding weights
        embedding_vector = embeddings_index.get(word)
        # and store inside the embedding matrix that we will train later on.
        if embedding_vector is not None:
            embedding_matrix[i] = embedding_vector
            embeddedCount += 1
    print('total embedded:', embeddedCount, 'common words')

    del(embeddings_index)
    gc.collect()

    print("Embedding matrix shape: ", embedding_matrix.shape)

    # Finally, return the embedding matrix
    return embedding_matrix
