import pandas as pd
import numpy as np
import torch
from torch import optim
import torch.nn as nn
import random
import math
import matplotlib.pyplot as plt
import time
from scipy.interpolate import interp1d
lossLastXUpdate = 5
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NUMBEROFPOINTPERGRAPH = 200
NUMBEROFGRAPHPERROW = 2
startTime = time.time()

class modelLineaire(nn.Module):
    def __init__(self):
        super().__init__()
        self.weights = nn.Parameter(torch.randn(1, 1))
        self.bias = nn.Parameter(torch.zeros(1))

    def forward(self, xb):
        z = self.weights * xb + self.bias
        return z

    def calculatePointForGraph(self, lineSpace):
        return np.add(np.multiply(lineSpace, self.weights.item()), self.bias.item())

    def __str__(self):
        return f"linear function with a: {self.weights.item()}, b: {self.bias.item()}"

    def appliedOnColumn(self, dfColumns):
        return dfColumns*self.weights.item() + self.bias.item()


class modelQuad(nn.Module):
    def __init__(self):
        super().__init__()
        # initialize all parameters that we will need
        self.weights1 = nn.Parameter(torch.randn(1, 1))
        self.weights2 = nn.Parameter(torch.randn(1, 1))
        self.bias1 = nn.Parameter(torch.zeros(1))

    def forward(self, xb):
        y = (self.weights1 * (xb) ** 2 +
             self.weights2 * (xb) +
             self.bias1)
        return y

    def calculatePointForGraph(self, lineSpace):
        return np.add(self.weights1.item() * np.multiply(lineSpace, lineSpace),
               np.add(self.weights2.item() * lineSpace,
                      self.bias1.item()))


    def __str__(self):
        return f"Quad function with a: {self.weights1.item()}, b: {self.weights2.item()}, c: {self.bias1.item()}"

    def appliedOnColumn(self, dfColumns):
        return dfColumns*dfColumns*self.weights1.item() + dfColumns*self.weights2.item() + self.bias1.item()

class modelCube(nn.Module):
    def __init__(self):
        super().__init__()
        # initialize all parameters that we will need
        self.weights1 = nn.Parameter(torch.randn(1, 1))
        self.weights2 = nn.Parameter(torch.randn(1, 1))
        self.weights3 = nn.Parameter(torch.randn(1, 1))
        self.bias1 = nn.Parameter(torch.zeros(1))

    def forward(self, xb):
        y = (self.weights1 * (xb) ** 3 +
             self.weights2 * (xb) ** 2 +
             self.weights3 * (xb) +
             self.bias1)
        return y

    def calculatePointForGraph(self, lineSpace):
        return np.add(self.weights1.item() * np.multiply(lineSpace, np.multiply(lineSpace, lineSpace)),
            np.add(self.weights2.item() * np.multiply(lineSpace, lineSpace),
               np.add(self.weights3.item() * lineSpace,
                      self.bias1.item())))

    def __str__(self):
        return f"cubic function with a: {self.weights1.item()}, b: {self.weights2.item()}, c: {self.weights3.item()}, d: {self.bias1.item()}"

    def appliedOnColumn(self, dfColumns):
        return dfColumns*dfColumns*dfColumns*self.weights2.item() + dfColumns*dfColumns*self.weights2.item() + dfColumns*self.weights3.item() + self.bias1.item()
def mse(y, y_hat):
    return ((y - y_hat) ** 2).mean()


def createFig(fig, point, pointPredBaseOnA, realValue, realValueMinusOtherPrediction, letter, nbRow, nbCol, index):
    currentFig = fig.add_subplot(nbRow, nbCol, index)
    currentFig.set_title(f"y based on {letter}")
    currentFig.plot(point, pointPredBaseOnA, label="Prediction")
    currentFig.scatter(realValue, realValueMinusOtherPrediction, label="trainData", color="red")
    currentFig.legend()

class Param:
    def __init__(self, letter, model, trainData):
        self.letter = letter
        self.model = model
        self.pandastrainData = trainData[letter]
        self.tensortrainData = torch.tensor(self.pandastrainData.values, dtype=torch.float32).view(-1, 1)
        self.lineSpace = np.linspace(min(self.pandastrainData), max(self.pandastrainData), NUMBEROFPOINTPERGRAPH)
    def reCalculateLineSpace(self):
        self.lineSpace = np.linspace(min(self.pandastrainData), max(self.pandastrainData), NUMBEROFPOINTPERGRAPH)

    def __str__(self):
        return f"{self.letter} with {self.model}"

    def appliedOnColumn(self, validationData):
        return self.model.appliedOnColumn(validationData[self.letter])

def normalized(x, mean, std):
    return (x - mean) / std


def plotEvolution(x, y, y_valid, tilte="loss evolution"):
    x=pd.Series(x)
    y=pd.Series(y)
    y_valid = pd.Series(y_valid)
    fig = plt.figure()
    currentFig = fig.add_subplot(1, 1, 1)
    x_new = np.linspace(x.min(), x.max(), 500)
    f = interp1d(x, y, kind='quadratic')
    y_smooth = f(x_new)
    f_valid = interp1d(x, y_valid, kind='quadratic')
    y_valid_smooth = f_valid(x_new)
    currentFig.plot(x_new, y_smooth, label="Training data")
    currentFig.plot(x_new, y_valid_smooth, label="Validation data")
    currentFig.scatter(x, y, label="Training data")
    currentFig.scatter(x, y_valid, label="Validation data")
    currentFig.legend()
    fig.suptitle(tilte)
    plt.show()

def train():
    i=0
    params = []
    for model in listModel:
        params.extend(model.model.parameters())
    opt = optim.Adam(params, lr=0.00005)  # lr = learning rate
    lastLoss = math.inf
    TARGETMAXLOSS = 1

    iteration = []
    lossHistory = []
    validationLossHistory = []
    while lastLoss> TARGETMAXLOSS:
        yPredict = 0
        for model in listModel:
            yPredict += model.model(model.tensortrainData)
        loss = mse(y, yPredict)
        loss.backward()
        opt.step()
        opt.zero_grad()
        i += 1
        if i % 10000 == 0 or loss < TARGETMAXLOSS:
            iteration.append(i)
            lossHistory.append(loss.data)
            validationError = calculateErrorOnValidationData()
            validationLossHistory.append(validationError)
            print(f"iter {i}, Loss = {loss.data}, deltaLoss = {lastLoss-loss.data}, elapseTime = {time.time()-startTime}, validationError = {validationError}")
            lastLoss = loss.data

            for model in listModel:
                print(model)
            print()
            for model in listModel:
                trainData["new"+model.letter] = model.pandastrainData.apply(model.model).apply(lambda x : x.item())
            #predict function

            fig = plt.figure()
            index = 0
            for model in listModel:
                index += 1
                yPredBaseOnModel = model.model.calculatePointForGraph(model.lineSpace)
                excludetrainData = 0
                for othermodel in listModel:
                    if othermodel.letter != model.letter:
                        excludetrainData+=trainData["new"+othermodel.letter]
                createFig(fig, model.lineSpace, yPredBaseOnModel, model.pandastrainData.values,
                          (comparedColumn-excludetrainData).values,
                          model.letter, NUMBEROFGRAPHPERROW ,numberOfColumnForGraph, index)
            fig.suptitle(f"iter {i}, Loss = {loss.data}, elapseTime = {round(time.time()-startTime)}")
            plt.legend()
            plt.show()
            if len(iteration)>=3:
                plotEvolution(iteration, lossHistory, validationLossHistory)
                if (len(iteration)>= lossLastXUpdate):
                    plotEvolution(iteration[-lossLastXUpdate:], lossHistory[-lossLastXUpdate:], validationLossHistory[-lossLastXUpdate:], f"loss of evolution of last {lossLastXUpdate} update")
def calculateErrorOnValidationData():
    data["prediction"] = sum([model.appliedOnColumn(validationData) for model in listModel])
    data["squarreError"] = (data["prediction"] - data["consumedElectric"])**2
    return data["squarreError"].mean()

if __name__ == "__main__":
    # generate trainDataset
    NUMBEROFPOINTFORAI = 1000
    data = pd.read_csv("transform/VED_trip_distance.csv")
    trainData = data.iloc[:int(len(data) * 0.8)]
    validationData = data.iloc[int(len(data) * 0.8):]
    comparedColumn = trainData[("consumedElectric")]
    y = torch.tensor(comparedColumn.values, dtype=torch.float32).view(-1, 1)

    listModel: list[Param] = [Param("speed", modelQuad(), trainData),
                              Param("slope", modelCube(), trainData),
                              Param("temperature", modelQuad(), trainData)]
    numberOfColumnForGraph = len(listModel) // NUMBEROFGRAPHPERROW + (len(listModel) % NUMBEROFGRAPHPERROW > 0)
    train()
