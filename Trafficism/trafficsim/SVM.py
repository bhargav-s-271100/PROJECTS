from sklearn.svm import SVC
from .read import read_data
import numpy as np
from time import time


class SVM:

    def __init__(self):
        
        x_train, x_test, y_train, y_test = read_data()
        self.model0 = SVC(kernel='linear')
        self.model1 = SVC(kernel='linear')
        self.model0.fit(x_train, y_train["useful"])
        self.model1.fit(x_train, y_train["rebroadcast"])
        print(
            f'SVM completed training. Accuracy: {min(self.model0.score(x_test, y_test["useful"]), self.model1.score(x_test, y_test["rebroadcast"]))*100}%')

    def predict(self, data):
        data = np.array(data).reshape(1, -1)
        return [self.model0.predict(data)[0], self.model1.predict(data)[0]]


if __name__ == '__main__':
    svm = SVM(X_train, X_test, Y_train, Y_test)
    
    times = []
    for i in range(X_train.shape[0]):
        t = time()
        svm.predict(X_train.iloc[i])
        times.append(time()-t)
    print(sum(times)/len(times))
