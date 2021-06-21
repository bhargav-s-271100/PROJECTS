import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.metrics import accuracy_score
from .read import read_data
from time import time


class ANN:

    def __init__(self, load=True, checkpoint_path="trafficsim/ANN/cp.ckpt"):
        x_train, x_test, y_train, y_test = read_data()
        x_train = np.asarray(x_train).astype(np.float32)
        x_test = np.asarray(x_test).astype(np.float32)
        y_train = np.asarray(y_train).astype('float32')
        y_test = np.asarray(y_test).astype('float32')

        self.model = tf.keras.Sequential()
        self.model.add(tf.keras.layers.Dense(512, activation='relu', input_shape=(7,)))
        self.model.add(tf.keras.layers.BatchNormalization())
        self.model.add(tf.keras.layers.Dropout(0.3))
        self.model.add(tf.keras.layers.Dense(128, activation='relu'))
        self.model.add(tf.keras.layers.BatchNormalization())
        self.model.add(tf.keras.layers.Dropout(0.25))
        self.model.add(tf.keras.layers.Dense(2, activation='sigmoid'))

        self.model.compile(loss='binary_crossentropy',
                  optimizer='adam', metrics=['accuracy'])
        if load:
            self.model.load_weights(checkpoint_path)
        else:
            cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                     save_weights_only=True,
                                                     verbose=1)
            self.model.fit(x_train, y_train, epochs=1000, callbacks=[cp_callback])

        loss, acc = self.model.evaluate(x_test, y_test, verbose=0)
        print(f'ANN Loaded. Accuracy: {acc}\tLoss: {loss}')


    def predict(self, data):
        data = np.array(data)
        return np.round(self.model.predict(data.reshape(-1, 7)).flatten()) == [1, 1]


if __name__ == '__main__':
    # main()
    X_train, X_test, Y_train, Y_test = read_data()
    ann = ANN(X_train, X_test, Y_train, Y_test, checkpoint_path="ANN/cp.ckpt")
    x_train = np.asarray(X_train).astype(np.float32)
    x_test = np.asarray(X_test).astype(np.float32)

    times = []
    for i in range(x_train.shape[0]):
        t = time()
        ann.predict(x_train[i])
        times.append(time()-t)
    print(sum(times)/len(times))
    