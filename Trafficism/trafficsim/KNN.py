from sklearn.neighbors import KNeighborsClassifier
from .read import read_data
import numpy as np
from time import time


class KNN:

    def __init__(self, n_neighbors):
        
        x_train, x_test, y_train, y_test = read_data()
        self.model = KNeighborsClassifier(n_neighbors=n_neighbors)
        self.model.fit(x_train, y_train)
        print(f'KNN completed training. Accuracy: {self.model.score(x_test, y_test)*100}%')

    def predict(self, data):
        data = np.array(data).reshape(1, -1)
        return self.model.predict(data).flatten()


if __name__ == '__main__':
    X_train, X_test, Y_train, Y_test = read_data()
    # for i in range(3, 27, 2):
    #     knn = KNN(X_train, X_test, Y_train, Y_test, i)
    knn = KNN(X_train, X_test, Y_train, Y_test, 7)

    times = []
    for i in range(X_train.shape[0]):
        t = time()
        knn.predict(X_train.iloc[i])
        times.append(time()-t)
    print(sum(times)/len(times))