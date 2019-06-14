from keras import layers
from keras.models import Sequential
from sklearn.utils import resample
import pandas as pd

trainable = True


def rebalance(data, random_seed):
    df_majority = data[data.target == 0]
    df_minority = data[data.target == 1]

    # Downsample majority class
    df_majority_downsampled = resample(df_majority,
                                       replace=False,    # sample without replacement
                                       # to match minority class
                                       n_samples=df_minority.shape[0],
                                       random_state=random_seed)  # reproducible results

    # Combine minority class with downsampled majority class
    data = pd.concat([df_majority_downsampled, df_minority])

    return data


def black_box(vocab_size, embedding_dim, embedding_matrix, maxlen):
    """
    Return a Keras fast-forward NN model with a embedding layer and two dense layers
    """
    model = Sequential()

    if embedding_matrix is not None:
        model.add(layers.Embedding(input_dim=vocab_size,
                                   output_dim=embedding_dim,
                                   weights=[embedding_matrix],
                                   input_length=maxlen,
                                   trainable=trainable),
                  )
    else:
        model.add(layers.Embedding(input_dim=vocab_size,
                                   output_dim=embedding_dim,
                                   input_length=maxlen,
                                   trainable=trainable),
                  )
    model.add(layers.GlobalMaxPool1D())
    model.add(layers.Dense(10, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    return model


def black_box_2(vocab_size, embedding_dim, embedding_matrix, maxlen, use_dropout=False):
    model = Sequential()
    if embedding_matrix is not None:
        model.add(layers.Embedding(input_dim=vocab_size,
                                   output_dim=embedding_dim,
                                   weights=[embedding_matrix],
                                   input_length=maxlen,
                                   trainable=trainable),
                  )
    else:
        model.add(layers.Embedding(input_dim=vocab_size,
                                   output_dim=embedding_dim,
                                   input_length=maxlen,
                                   trainable=trainable),
                  )
    model.add(layers.Dropout(0.2))

    # we add a Convolution1D, which will learn filters
    # word group filters of size filter_length:
    model.add(layers.Conv1D(32,
                            4,
                            padding='valid',
                            activation='relu',
                            strides=1))
    # we use max pooling:
    model.add(layers.GlobalMaxPooling1D())

    # We add a vanilla hidden layer:
    model.add(layers.Dense(32))
    model.add(layers.Dropout(0.2))
    model.add(layers.Activation('relu'))

    # We project onto a single unit output layer, and squash it with a sigmoid:
    model.add(layers.Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    return model


def black_box_3(vocab_size, embedding_dim, embedding_matrix, maxlen, use_dropout=False):
    model = Sequential()
    if embedding_matrix is not None:
        model.add(layers.Embedding(input_dim=vocab_size,
                                   output_dim=embedding_dim,
                                   weights=[embedding_matrix],
                                   input_length=maxlen,
                                   trainable=trainable),
                  )
    else:
        model.add(layers.Embedding(input_dim=vocab_size,
                                   output_dim=embedding_dim,
                                   input_length=maxlen,
                                   trainable=trainable),
                  )

    model.add(layers.Dropout(0.25))
    model.add(layers.Conv1D(64,
                            3,
                            padding='valid',
                            activation='relu',
                            strides=1))
    model.add(layers.MaxPooling1D(pool_size=4))
    model.add(layers.LSTM(70))
    model.add(layers.Dense(1))
    model.add(layers.Activation('sigmoid'))

    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    return model


def black_box_4(vocab_size, embedding_dim, embedding_matrix, maxlen):
    """
    Return a Keras fast-forward NN model with a embedding layer and two dense layers
    """
    model = Sequential()

    if embedding_matrix is not None:
        model.add(layers.Embedding(input_dim=vocab_size,
                                   output_dim=embedding_dim,
                                   weights=[embedding_matrix],
                                   input_length=maxlen,
                                   trainable=trainable),
                  )
    else:
        model.add(layers.Embedding(input_dim=vocab_size,
                                   output_dim=embedding_dim,
                                   input_length=maxlen,
                                   trainable=trainable),
                  )
    model.add(layers.Dense(400, activation='relu'))
    model.add(layers.GlobalMaxPool1D())
    model.add(layers.Dense(200, activation='relu'))
    model.add(layers.Dense(10, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    return model


def accuracy(model, history, X_train, y_train, X_test, y_test, table_temp, model_name):
    loss, accuracy = model.evaluate(X_train, y_train, verbose=True)
    print("Training Accuracy: {:.4f}".format(accuracy))

    table_temp[model_name + '_train_acc'] = round(accuracy, 4)

    loss, accuracy = model.evaluate(X_test, y_test, verbose=True)

    print("Testing Accuracy:  {:.4f}".format(accuracy))

    table_temp[model_name + '_test_acc'] = round(accuracy, 4)

    return table_temp
