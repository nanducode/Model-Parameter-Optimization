from os import listdir
from os.path import isfile, join
import keras
import pandas as pd
from keras import models
from keras import layers
from keras import optimizers
import numpy as np

def get_training_data(path):
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    train_targets = []
    train_data = []
    test_targets = []
    test_data = []
    counter = 1
    for f in onlyfiles:
        # remove first ten years of simulations
        if not (f.endswith("_0.csv") or f.endswith("_1.csv")):
            KH = f.split("_")[0]
            dataset = pd.read_csv(path + f)
            if counter != 8:
                train_targets.append(KH)
                train_data.append(np.array(dataset, ndmin=2))
                counter += 1
            else:
                test_targets.append(KH)
                test_data.append(np.array(dataset, ndmin=2))
                counter = 1

    # put into numpy arrays
    train_data = np.array(train_data, ndmin=3)
    test_data = np.array(test_data, ndmin=3)
    train_targets = np.array(train_targets)
    test_targets = np.array(test_targets)

    #randomly permute training data
    p = np.random.permutation(len(train_data))
    train_data = train_data[p]
    train_targets = train_targets[p]

    return train_data, train_targets, test_data, test_targets

def build_model():

    model = models.Sequential()
    model.add(layers.Dense(256, activation='relu',
                           input_shape=(train_data.shape[1], train_data.shape[2])))
    model.add(layers.Dropout(.5))
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dropout(.5))
    model.add(layers.Flatten())
    model.add(layers.Dense(1))
    sgd = optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True, clipnorm=1.)
    model.compile(optimizer=sgd, loss='mse', metrics=['mae'])
    return model


train_data, train_targets, test_data, test_targets = get_training_data(
    "/Users/spartee/Dropbox/Professional/Cray/399-Thesis/MPO/data/")


# Get a fresh, compiled model.
model = build_model()
# Train it on the entirety of the data.
model.fit(train_data, train_targets,
          epochs=40, batch_size=128, verbose=1)
test_mse_score, test_mae_score = model.evaluate(test_data, test_targets)
print(test_mse_score)
print(test_mae_score)

