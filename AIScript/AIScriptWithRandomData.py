import pandas as pd
import numpy as np
import torch
from torch import optim
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
from torch.nn import Linear, MSELoss, functional as F
import random
import math
import matplotlib.pyplot as plt
import time
from scipy.interpolate import interp1d

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
def mse(y, y_hat):
    return ((y - y_hat) ** 2).mean()


def createFig(fig, point, pointPredBaseOnA, realValue, realValueMinusOtherPrediction, letter, nbRow, nbCol, index):
    currentFig = fig.add_subplot(nbRow, nbCol, index)
    currentFig.set_title(f"y based on {letter}")
    currentFig.plot(point, pointPredBaseOnA, label="Prediction")
    currentFig.scatter(realValue, realValueMinusOtherPrediction, label="Data", color="red")
    currentFig.legend()

class Param:
    def __init__(self, letter, model, data):
        self.letter = letter
        self.model = model
        self.pandasData = data[letter]
        self.tensorData = torch.tensor(self.pandasData.values, dtype=torch.float32).view(-1, 1)
        self.lineSpace = np.linspace(min(self.pandasData), max(self.pandasData), NUMBEROFPOINTPERGRAPH)
    def reCalculateLineSpace(self):
        self.lineSpace = np.linspace(min(self.pandasData), max(self.pandasData), NUMBEROFPOINTPERGRAPH)


def normalized(x, mean, std):
    return (x - mean) / std


#generate dataset
NUMBEROFPOINTFORAI = 1000
data = pd.DataFrame(pd.Series(np.random.randint(-1000, 1000, size=NUMBEROFPOINTFORAI)), columns=['c'])
data["d"] = np.random.randint(-1000, 1000, size=NUMBEROFPOINTFORAI)
data["a"] = np.random.randint(-1000, 1000, size=NUMBEROFPOINTFORAI)
data["b"] = np.random.randint(-1000, 1000, size=NUMBEROFPOINTFORAI)
data["e"] = np.random.randint(-1000, 1000, size=NUMBEROFPOINTFORAI)
data["f"] = np.random.randint(-1000, 1000, size=NUMBEROFPOINTFORAI)

data["a"] = data["a"].apply(lambda x: normalized(x, data["a"].mean(), data["a"].std()))
data["b"] = data["b"].apply(lambda x: normalized(x, data["b"].mean(), data["b"].std()))
data["c"] = data["c"].apply(lambda x: normalized(x, data["c"].mean(), data["c"].std()))
data["d"] = data["d"].apply(lambda x: normalized(x, data["d"].mean(), data["d"].std()))
data["e"] = data["e"].apply(lambda x: normalized(x, data["e"].mean(), data["e"].std()))
data["f"] = data["f"].apply(lambda x: normalized(x, data["f"].mean(), data["f"].std()))

data["y"] = (random.randint(-50, 50) * data["a"] ** 3 +
              random.randint(-50, 50) * data["a"] ** 2 +
              random.randint(-50, 50) * data["a"] +
              random.randint(-50, 50)+
              random.randint(-50, 50) * data["b"] ** 3 +
              random.randint(-50, 50) * data["b"] ** 2 +
              random.randint(-50, 10) * data["b"] +
              random.randint(-50, 50)+
              (random.randint(-50, 10) * data["c"] ** 2 +
              random.randint(-50, 50) * data["c"] +
              random.randint(-50, 50)) +
              random.randint(-50, 50) * data["d"] ** 2 +
              random.randint(-50, 50) * data["d"] +
              random.randint(-50, 50) +
              random.randint(-50, 50) * data["e"] +
              random.randint(-50, 50) * data["f"])



y = torch.tensor(data["y"].values, dtype=torch.float32).view(-1, 1)

listModel: list[Param] = [Param("a",modelCube(), data),
                          Param("b", modelCube(), data),
                          Param("c", modelQuad(), data),
                          Param("d",modelQuad(), data),
                          Param("e", modelLineaire(), data),
                          Param("f", modelLineaire(), data),]
numberOfColumnForGraph = len(listModel)//NUMBEROFGRAPHPERROW + (len(listModel)%NUMBEROFGRAPHPERROW >0)
params = []
for model in listModel:
    params.extend(model.model.parameters())
opt = optim.Adam(params, lr=0.0005)  #lr = learning rate
lastLoss = math.inf
i = 0
TARGETMAXLOSS = 10E-6

iteration = []
lossHistory = []


def plotEvolution(x, y):
    x=pd.Series(x)
    y=pd.Series(y)
    fig = plt.figure()
    currentFig = fig.add_subplot(1, 1, 1)
    x_new = np.linspace(x.min(), x.max(), 500)
    f = interp1d(x, y, kind='quadratic')
    y_smooth = f(x_new)
    currentFig.plot(x_new, y_smooth)
    currentFig.scatter(x, y)
    fig.suptitle("loss evolution")
    plt.show()


while lastLoss> TARGETMAXLOSS:
    yPredict = 0
    for model in listModel:
        yPredict += model.model(model.tensorData)
    loss = mse(y, yPredict)
    loss.backward()
    opt.step()
    opt.zero_grad()
    i += 1
    if i % 10000 == 0 or loss < TARGETMAXLOSS:
        iteration.append(i)
        lossHistory.append(loss.data)
        print(f"iter {i}, Loss = {loss.data}, deltaLoss = {lastLoss-loss.data}, elapseTime = {time.time()-startTime}")
        lastLoss = loss.data

        """for param in params:
            if param.requires_grad:
                print(param.data.item())
        print()"""
        for model in listModel:
            data["new"+model.letter] = model.pandasData.apply(model.model).apply(lambda x : x.item())
        #predict function

        fig = plt.figure()
        index = 0
        for model in listModel:
            index += 1
            yPredBaseOnModel = model.model.calculatePointForGraph(model.lineSpace)
            excludeData = 0
            for othermodel in listModel:
                if othermodel.letter != model.letter:
                    excludeData+=data["new"+othermodel.letter]
            createFig(fig, model.lineSpace, yPredBaseOnModel, model.pandasData.values,
                      (data["y"]-excludeData).values,
                      model.letter, NUMBEROFGRAPHPERROW ,numberOfColumnForGraph, index)
        fig.suptitle(f"iter {i}, Loss = {loss.data}, elapseTime = {round(time.time()-startTime)}")
        plt.legend()
        plt.show()
        if len(iteration)>=3:
            plotEvolution(iteration, lossHistory)

