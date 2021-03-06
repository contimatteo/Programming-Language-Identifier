# /usr/bin/env python3

from dataset import DatasetManager
from utils import FileManager
import pandas as pd
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers.core import Dense
from keras.layers.embeddings import Embedding
from keras.layers import Conv1D, MaxPooling1D
from keras.layers import Dropout
from keras.layers.recurrent import LSTM
from sklearn.model_selection import train_test_split
import os
import json


def main():
    # load the dataset
    datasetManager = DatasetManager()
    datasetManager.initialize('CNN').load()

    #

    counter = 0
    code_archive = []
    languages = []

    for languageFolder in FileManager.getLanguagesFolders(FileManager.datasets['training']['url']):
        for exampleFolder in FileManager.getExamplesFolders(languageFolder.path):
            originalFileUrl = FileManager.getOriginalFileUrl(exampleFolder.path)
            originalFileContent = FileManager.readFile(originalFileUrl)
            #
            counter += 1
            code_archive.append(originalFileContent)
            languages.append(str(languageFolder.name).lower())

    # added - and @
    max_fatures = 100000
    embed_dim = 128
    lstm_out = 64
    batch_size = 32
    epochs = 30
    test_size = 0.001

    tokenizer = Tokenizer(num_words=max_fatures)
    tokenizer.fit_on_texts(code_archive)
    dictionary = tokenizer.word_index
    FileManager.createFile(os.path.join(FileManager.getRootUrl(), 'tmp/wordindex.json'), json.dumps(dictionary))

    X = tokenizer.texts_to_sequences(code_archive)
    X = pad_sequences(X, 100)
    Y = pd.get_dummies(languages)
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=test_size)

    # LSTM model
    model = Sequential()
    model.add(Embedding(max_fatures, embed_dim, input_length=100))
    model.add(Conv1D(filters=128, kernel_size=3, padding='same', dilation_rate=1, activation='relu'))
    model.add(MaxPooling1D(pool_size=4))
    model.add(Conv1D(filters=64, kernel_size=3, padding='same', dilation_rate=1, activation='relu'))
    model.add(MaxPooling1D(pool_size=2))
    model.add(LSTM(lstm_out))
    model.add(Dropout(0.5))
    model.add(Dense(64))
    model.add(Dense(len(Y.columns), activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    history = model.fit(X_train, Y_train, epochs=epochs, batch_size=batch_size)

    model.save(os.path.join(FileManager.getRootUrl(), 'tmp/code_model.h5'))
    model.save_weights(os.path.join(FileManager.getRootUrl(), 'tmp/code_model_weights.h5'))

    score, acc = model.evaluate(X_test, Y_test, verbose=2, batch_size=batch_size)
    print(model.metrics_names)
    print("Validation loss: %f" % score)
    print("Validation acc: %f" % acc)

##


if __name__ == "__main__":
    main()

