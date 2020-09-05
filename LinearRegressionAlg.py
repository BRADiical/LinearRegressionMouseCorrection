import tensorflow
import keras
import numpy as np
import pandas as pd
import sklearn
from sklearn import linear_model
from sklearn.utils import shuffle
import matplotlib.pyplot as pyplot
import pickle
from matplotlib import style
import csv

import pygame
import pyautogui



def trainLinearModel(filename):
    advancedData = pd.read_csv(filename, sep=";")
    print("ADVANCED_DATA_AFTER_CSV_READ = ")
    #print(advancedData)
    #advancedData = advancedData[['Time_Stamp', 'MouseX', 'MouseY', 'Target_LocationX', 'Target_LocationY',
    #                             'Intended_Direction', 'Target_Distance', 'Observed_Distance',
    #                             'Observed_Speed', 'Observed_Direction', 'Directional_Error',
    #                             'Distance_Of_Error', 'Recent_Average_Direction', 'Recent_Average_Speed']]
    #print("ADVANCED_DATA_AFTER_INDEX_ADDITION = ")
    #print(advancedData)
    predict = ["Target_Distance", "Intended_Direction"]

    x = np.array(advancedData.drop(["Intended_Direction", "Target_Distance",
                                    "Target_LocationX", "Target_LocationY",
                                    "Directional_Error", "Distance_Of_Error"], 1))
    print("ADVANCED DATA AFTER NUMPY = ")
    print(x)
    y = np.array(advancedData[predict])

    best = 0
    for _ in range(5000):
        x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(x, y, test_size=0.1)
        linear = linear_model.LinearRegression()

        linear.fit(x_train, y_train)
        accuracy = linear.score(x_test, y_test)

        if accuracy > best:
            best = accuracy
            with open(filename + ".pickle", "wb") as f:
                pickle.dump(linear, f)

    print("Best Accuracy: ", best)

    pickle_in = open(filename + ".pickle", "rb")
    linear = pickle.load(pickle_in)

    errorCoef = getAverageError(filename)
    return best, errorCoef

def graphOneToOneRelationship(x,y):
    sampleData = pd.read_csv("testData_advanced", sep=";")
    sampleData = sampleData[['Time_Stamp', 'MouseX', 'MouseY', 'Target_LocationX', 'Target_LocationY',
                             'Intended_Direction', 'Target_Distance', 'Observed_Distance',
                             'Observed_Speed', 'Observed_Direction', 'Directional_Error',
                             'Distance_Of_Error', 'Recent_Average_Direction', 'Recent_Average_Speed']]
    style.use("ggplot")
    pyplot.scatter(sampleData[x], sampleData[y], s=3)
    pyplot.xlabel(x)
    pyplot.ylabel(y)
    pyplot.show()

def getAverageError(filename):
    advancedData = pd.read_csv(filename, sep=";")
    advancedData = advancedData[['Time_Stamp', 'MouseX', 'MouseY', 'Target_LocationX', 'Target_LocationY',
                                 'Intended_Direction', 'Target_Distance', 'Observed_Distance',
                                 'Observed_Speed', 'Observed_Direction', 'Directional_Error',
                                 'Distance_Of_Error', 'Recent_Average_Direction', 'Recent_Average_Speed']]
    rows = np.array(advancedData)
    line_count = 0
    error_sum = 0
    for row in rows:
        if line_count == 0:
            line_count += 1
        else:
            error_sum += row[11]
            line_count += 1

    return error_sum/line_count
