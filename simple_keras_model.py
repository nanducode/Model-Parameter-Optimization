
import keras
import pandas as pd
from keras import models
from keras import layers
from keras import optimizers
import numpy as np
from preProcessing import get_training_data

def build_model():

    model = models.Sequential()
    model.add(layers.Dense(256, activation='tanh',
                           input_shape=(train_data.shape[1], train_data.shape[2])))
    model.add(layers.Dropout(.05))
    model.add(layers.Dense(128, activation="tanh"))
    model.add(layers.Flatten())
    model.add(layers.Dense(1))
    #sgd = optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True, clipnorm=.9)
    model.compile(optimizer="adam", loss='logcosh', metrics=['mae', 'mse'])
    return model


train_data, train_targets, test_data, test_targets = get_training_data(
    "/Users/spartee/Dropbox/Professional/Cray/399-Thesis/MPO/data-5yr-avg/")



# Get a fresh, compiled model.
model = build_model()
# Train it on the entirety of the data.
model.fit(train_data, train_targets,
          epochs=80, batch_size=10, verbose=1, validation_split=.2)
test_score = model.evaluate(test_data, test_targets)

print(test_score)

