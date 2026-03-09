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


class modelLineaire(nn.Module):
    def __init__(self):
        super().__init__()
        self.weights = nn.Parameter(torch.randn(1, 1))
        self.bias = nn.Parameter(torch.zeros(1))

    def forward(self, xb):
        z = self.weights * xb + self.bias
        return z


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


def mse(y, y_hat):
    return ((y - y_hat) ** 2).mean()


def createFig(fig, index, point, pointPredBaseOnA, realValue, realValueMinusOtherPrediction):
    currentFig = fig.add_subplot(1, 3, index)
    currentFig.set_title(f"y based on a")
    currentFig.plot(point, pointPredBaseOnA, label="Function predicted")
    currentFig.scatter(realValue, realValueMinusOtherPrediction, label="Data", color="red")
    currentFig.legend()


#generate dataset
NUMBEROFPOINTFORAI = 100
data = pd.DataFrame(pd.Series(np.random.randint(-1000, 1000, size=NUMBEROFPOINTFORAI)), columns=['x'])
data["z"] = np.random.randint(-1000, 1000, size=NUMBEROFPOINTFORAI)
data["a"] = np.random.randint(-1000, 1000, size=NUMBEROFPOINTFORAI)
data["y"] = ((random.randint(-50, 50) * data["x"] ** 2 +
              random.randint(-50, 50) * data["x"] +
              random.randint(-50, 50)) +
             random.randint(-50, 50) * data["z"] +
             random.randint(-50, 50) * data["a"])

x = torch.tensor(data["x"].values, dtype=torch.float32).view(-1, 1)
y = torch.tensor(data["y"].values, dtype=torch.float32).view(-1, 1)
z = torch.tensor(data["z"].values, dtype=torch.float32).view(-1, 1)
a = torch.tensor(data["a"].values, dtype=torch.float32).view(-1, 1)

modelX = modelQuad()
modelZ = modelLineaire()
modelA = modelLineaire()
params = list(modelX.parameters()) + list(modelZ.parameters()) + list(modelA.parameters())
opt = optim.Adam(params, lr=5e2)  #lr = learning rate
lastLoss = math.inf
i = 0
data.sort_values('x', inplace=True)
TARGETMAXLOSS = 1000
while lastLoss > TARGETMAXLOSS:
    yPredict = modelX(x) + modelZ(z) + modelA(a)
    loss = mse(y, yPredict)
    loss.backward()
    opt.step()
    opt.zero_grad()
    i += 1
    if i % 10000 == 0 or loss < TARGETMAXLOSS:
        lastLoss = loss.data
        print(f"iter {i}, Loss = {loss.data}")
        for param in params:
            if param.requires_grad:
                print(param.data.item())
        print()
        data["newZ"] = data["z"].apply(modelZ).apply(lambda x: x.item())
        data["newX"] = data["x"].apply(modelX).apply(lambda x: x.item())
        data["newA"] = data["a"].apply(modelA).apply(lambda x: x.item())
        #predict function
        numberOfPointInGraphToDoTheLine = 200
        xGraph = np.linspace(min(data["x"]), max(data["x"]), numberOfPointInGraphToDoTheLine)
        zGraph = np.linspace(min(data["z"]), max(data["z"]), numberOfPointInGraphToDoTheLine)
        aGraph = np.linspace(min(data["a"]), max(data["a"]), numberOfPointInGraphToDoTheLine)

        yPredBaseOnX = np.add(params[0].data.item() * np.multiply(xGraph, xGraph),
                              np.add(params[1].data.item() * xGraph,
                                     params[2].data.item()))
        yPredBaseOnZ = np.add(np.multiply(zGraph, params[3].data.item()), params[4].data.item())
        yPredBaseOnA = np.multiply(aGraph, params[5].data.item())
        yGraph = np.add(np.add(yPredBaseOnX, yPredBaseOnZ), yPredBaseOnA)

        fig = plt.figure()
        createFig(fig, 1, xGraph, yPredBaseOnX, data["x"].values, (data["y"] - data["newZ"] - data["newA"]).values)
        createFig(fig, 2, zGraph, yPredBaseOnZ, data["z"].values, (data["y"] - data["newX"] - data["newA"]).values)
        createFig(fig, 3, aGraph, yPredBaseOnA, data["a"].values, (data["y"] - data["newX"] - data["newZ"]).values)
        fig.suptitle(f"iter {i}, Loss = {loss.data}")
        plt.show()
