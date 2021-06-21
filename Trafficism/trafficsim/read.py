from sklearn.model_selection import train_test_split
import pandas as pd


def read_data():
    dataset = pd.read_csv("data.csv")

    predictors = dataset.drop(["useful", "rebroadcast"], axis=1)
    target = dataset[["useful", "rebroadcast"]]

    return train_test_split(predictors, target, test_size=0.20, random_state=0)
