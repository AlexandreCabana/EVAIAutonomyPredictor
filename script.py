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
numberOfPointInGraphToDoTheLine = 200
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
        y = (self.weights3 * (xb) ** 3 +
             self.weights2 * (xb) ** 2 +
             self.weights3 * (xb) +
             self.bias1)
        return y

    def calculatePointForGraph(self, lineSpace):
        print(f"a={self.weights1.item()}, b={self.weights2.item()}, c={self.weights3.item()}, d={self.bias1.item()}")
        return np.add(self.weights1.item() * np.multiply(lineSpace, np.multiply(lineSpace, lineSpace)),
            np.add(self.weights2.item() * np.multiply(lineSpace, lineSpace),
               np.add(self.weights3.item() * lineSpace,
                      self.bias1.item())))
def mse(y, y_hat):
    return ((y - y_hat) ** 2).mean()


def createFig(fig, index, point, pointPredBaseOnA, realValue, realValueMinusOtherPrediction, letter):
    currentFig = fig.add_subplot(1, 4, index)
    currentFig.set_title(f"y based on {letter}")
    currentFig.plot(point, pointPredBaseOnA, label="Function predicted")
    currentFig.scatter(realValue, realValueMinusOtherPrediction, label="Data", color="red")
    currentFig.legend()

class Param:
    def __init__(self, letter, model, data):
        self.letter = letter
        self.model = model
        self.pandasData = data[letter]
        self.tensorData = torch.tensor(self.pandasData.values, dtype=torch.float32).view(-1, 1)
        self.lineSpace = np.linspace(min(self.pandasData), max(self.pandasData), numberOfPointInGraphToDoTheLine)
    def reCalculateLineSpace(self):
        self.lineSpace = np.linspace(min(self.pandasData), max(self.pandasData), numberOfPointInGraphToDoTheLine)


def normalized(x, mean, std):
    return (x - mean) / std


#generate dataset
NUMBEROFPOINTFORAI = 1000
data = pd.DataFrame(pd.Series(np.random.randint(-1000, 1000, size=NUMBEROFPOINTFORAI)), columns=['x'])
data["z"] = np.random.randint(-1000, 1000, size=NUMBEROFPOINTFORAI)
data["a"] = np.random.randint(-1000, 1000, size=NUMBEROFPOINTFORAI)
data["b"] = np.random.randint(-1000, 1000, size=NUMBEROFPOINTFORAI)

data["x"] = data["x"].apply(lambda x: normalized(x, data["x"].mean(), data["x"].std()))
data["z"] = data["z"].apply(lambda x: normalized(x, data["z"].mean(), data["z"].std()))
data["a"] = data["a"].apply(lambda x: normalized(x, data["a"].mean(), data["a"].std()))
data["b"] = data["b"].apply(lambda x: normalized(x, data["b"].mean(), data["b"].std()))

data["y"] = (0 * data["b"] ** 3 +
              (random.randint(-10, 0) * data["b"] ** 2 +
              random.randint(-50, 50) * data["b"] +
              random.randint(-50, 50))+
             (random.randint(-50, 10) * data["x"] ** 2 +
              random.randint(-50, 50) * data["x"] +
              random.randint(-50, 50)) +
             random.randint(-50, 50) * data["z"] +
             random.randint(-50, 50) * data["a"])



y = torch.tensor(data["y"].values, dtype=torch.float32).view(-1, 1)

listModel: list[Param] = [Param("x",modelQuad(), data),
                          Param("z", modelLineaire(), data),
                          Param("a", modelLineaire(), data),
                          Param("b",modelCube(), data)]

listModel: list[Param] = [Param("x",modelQuad(), data),
                          Param("z", modelLineaire(), data),
                          Param("a", modelLineaire(), data),
                          Param("b",modelQuad(), data)]

params = []
for model in listModel:
    params.extend(model.model.parameters())
opt = optim.Adam(params, lr=0.0005)  #lr = learning rate
lastLoss = math.inf
i = 0
TARGETMAXLOSS = 0.25

iteration = []
lossHistory = []
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
        """
        for param in params:
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
            createFig(fig, index, model.lineSpace, yPredBaseOnModel, model.pandasData.values,
                      (data["y"]-excludeData).values,
                      model.letter)
        fig.suptitle(f"iter {i}, Loss = {loss.data}, elapseTime = {round(time.time()-startTime)}")
        plt.show()
        fig = plt.figure()
        currentFig = fig.add_subplot(1, 1, 1)
        currentFig.scatter(iteration, lossHistory, label="Data", color="red")
        fig.suptitle("loss evolution")
        plt.legend()

