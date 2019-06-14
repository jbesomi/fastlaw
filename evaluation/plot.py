import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve

OUTPUT_FOLDER = 'results/'


def filename(OUTPUT_FOLDER, slug, num_train_cases, log_time, kind):
    return OUTPUT_FOLDER + slug + "/" + str(num_train_cases) + "/" + log_time + "_" + kind + ".png"


def save_loss(history_random, history_fasttext, history_fastlaw, num_train_cases, slug, log_time):
    loss_random = history_random.history['loss']
    loss_fasttext = history_fasttext.history['loss']
    loss_fastlaw = history_fastlaw.history['loss']

    x = range(1, len(loss_random) + 1)

    plt.figure(figsize=(12, 5))

    plt.plot(x, loss_random, label='random initialization')
    plt.plot(x, loss_fasttext, label='fasttext')
    plt.plot(x, loss_fastlaw, label='fastlaw')

    plt.title(slug.capitalize() + ": loss random init. vs. Fastlaw vs. Fasttext on " +
              str(num_train_cases) + " trained cases")

    plt.legend()

    plt.savefig(filename(OUTPUT_FOLDER, slug,
                         num_train_cases, log_time, 'loss'))
    plt.close('all')


def save_acc(history_random, history_fasttext, history_fastlaw, num_train_cases, slug, log_time):
    f1_random = history_random.history['acc']
    f1_fasttext = history_fasttext.history['acc']
    f1_fastlaw = history_fastlaw.history['acc']

    x = range(1, len(f1_random) + 1)

    plt.figure(figsize=(12, 5))

    plt.plot(x, f1_random, label='random initialization')
    plt.plot(x, f1_fasttext, label='fasttext')
    plt.plot(x, f1_fastlaw, label='fastlaw')

    plt.title(slug.capitalize() + ": accuracy random init. vs. Fastlaw vs. Fasttext on " +
              str(num_train_cases) + " trained cases")
    plt.legend()
    plt.savefig(filename(OUTPUT_FOLDER, slug,
                         num_train_cases, log_time, 'acc'))
    plt.close('all')


def save_val_acc(history_random, history_fasttext, history_fastlaw, num_train_cases, slug, log_time):
    f1_random = history_random.history['val_acc']
    f1_fasttext = history_fasttext.history['val_acc']
    f1_fastlaw = history_fastlaw.history['val_acc']

    x = range(1, len(f1_random) + 1)

    plt.figure(figsize=(12, 5))

    plt.plot(x, f1_random, label='random initialization')
    plt.plot(x, f1_fasttext, label='fasttext')
    plt.plot(x, f1_fastlaw, label='fastlaw')

    plt.title(slug.capitalize() + ": val. Acc. random init. vs. Fastlaw vs. Fasttext on " +
              str(num_train_cases) + " trained cases")
    plt.legend()
    plt.savefig(filename(OUTPUT_FOLDER, slug,
                         num_train_cases, log_time, 'val_acc'))
    plt.close('all')


def save_aucroc(model_random, model_fasttext, model_fastlaw, X_test, y_test, num_train_cases, num_ones, slug, log_time):
    plt.figure(figsize=(12, 5))
    plt.plot([0, 1], [0, 1], linestyle='--')  # diagonal line

    fpr_random, tpr_random, _ = roc_curve(y_test, model_random.predict(X_test))
    # plot the roc curve for the model
    plt.plot(fpr_random, tpr_random, marker='.', label='random initialization')

    fpr_fasttext, tpr_fasttext, _ = roc_curve(
        y_test, model_fasttext.predict(X_test))
    # plot the roc curve for the model
    plt.plot(fpr_fasttext, tpr_fasttext, marker='.', label='fasttext')

    fpr_fastlaw, tpr_fastlaw, _ = roc_curve(
        y_test, model_fastlaw.predict(X_test))
    # plot the roc curve for the model
    plt.plot(fpr_fastlaw, tpr_fastlaw, marker='.', label='fastlaw')

    plt.title(slug.capitalize() + ": AUC-ROC curve random init. vs. Fastlaw vs. Fasttext on " +
              str(num_train_cases) + " trained cases")
    plt.legend()

    plt.savefig(filename(OUTPUT_FOLDER, slug,
                         num_train_cases, log_time, 'aucroc'))
    plt.close('all')
