import numpy as np 
import matplotlib.pyplot as plt
from keras import models
from keras import layers
#import csv
#from sklearn.utils import shuffle
#from keras import optimizers
#from numpy.lib.npyio import savetxt
#from tensorflow.python.keras.layers.embeddings import Embedding
#from tensorflow.python.keras.layers.recurrent import SimpleRNN

file = open('df_text_eng.csv', 'r', encoding = 'utf-8')
file = file.readlines()

"""
Creates vocabulary from training data. Will condense the vocabulary to a user-specified minimum number of 
occurances for each word. A non-condensed vocabulary would be far too large given the number of training
data samples. 
"""
def generateVocabulary(minOccurances):
    vocabulary = {}
    for line in file:
        line = line.split()
        for word in line[1:-1]:
            if word in vocabulary.keys():
                vocabulary[word] += 1
            else:
                vocabulary[word] = 1

    vocabulary_refined = []
    for word in vocabulary.keys():
        if vocabulary[word] > minOccurances:
            vocabulary_refined.append(word)
    return vocabulary_refined


"""
Creates 2D numpy array which will hold the labels for each sample.
"""
def createMatrix(vocab, cutoff):
    return np.zeros((cutoff, len(vocab)), dtype = int)

def condenseData(m, t):
    matrix = []
    targets = []
    for i in range(len(m)):
        has1 = False
        for num in m[i]:
            if num == 1:
                has1 = True
        if has1:
            matrix.append(m[i])
            targets.append(t[i])
    return np.asarray(matrix), np.asarray(targets)


def populateTrainMatrix(vocab, matrix):
    targets = []
    for i in range(len(matrix)):
        line = file[i].split("\",\" ")
        targets.append(-1)
        try:
            for word in line[1].split():
                if word in vocab:
                    matrix[i][vocab.index(word)] = 1
            if line[2][:-2] == 'failed':
                targets[i] = 0
            else:
                targets[i] = 1
        except IndexError:
            continue
    return condenseData(matrix, targets)


def createTestMatrix(vocab, cutoff):
    return np.zeros((len(file) - cutoff, len(vocab)), dtype = int)


def populateTestMatrix(vocab, matrix, cutoff):
    targets = []
    for i in range(len(file) - len(matrix)):
        line = file[i + len(matrix)].split("\",\" ")
        targets.append(-1)
        try:
            for word in line[1].split():
                if word in vocab:
                    matrix[i][vocab.index(word)] = 1
            if line[2][:-2] == 'failed':
                targets[i] = 0
            else:
                targets[i] = 1
        except IndexError:
            continue
    return condenseData(matrix, targets)


"""
Creates keras model
"""
def createModel(cutoff, vocab_length):
    model = models.Sequential()
    
    model.add(layers.Dense(16, activation = 'relu', input_shape = (cutoff,vocab_length)))
    model.add(layers.Dense(8, activation = 'relu'))
    model.add(layers.Dense(1, activation = 'sigmoid'))

    model.compile(optimizer = 'rmsprop', loss = 'binary_crossentropy', metrics = ['acc'])

    return model

"""
Trains keras model with the training data and evaluates with the test data
"""
def trainAndEvaluate(model, train_matrix, train_targets, test_matrix, test_targets):
    history = model.fit(train_matrix, train_targets, epochs = 15, batch_size = 500, validation_data = (train_matrix, train_targets))
    # summarize history for accuracy
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()
    
    # summarize history for loss
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()
    results = model.evaluate(test_matrix, test_targets)


def main():
    vocab = generateVocabulary(300)
    cutoff = int(len(file) * 0.7)
    train_matrix = createMatrix(vocab, cutoff)
    train_matrix, train_targets = populateTrainMatrix(vocab, train_matrix)

    test_matrix = createTestMatrix(vocab, cutoff)
    test_matrix, test_targets = populateTestMatrix(vocab, test_matrix, cutoff)

    model = createModel(cutoff, len(vocab))

    trainAndEvaluate(model, train_matrix, train_targets, test_matrix, test_targets)
    
main()