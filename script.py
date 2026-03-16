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

numberOfPointInGraphToDoTheLine = 200

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


def mse(y, y_hat):
    return ((y - y_hat) ** 2).mean()


def createFig(fig, index, point, pointPredBaseOnA, realValue, realValueMinusOtherPrediction, letter):
    currentFig = fig.add_subplot(1, 3, index)
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


y = torch.tensor(data["y"].values, dtype=torch.float32).view(-1, 1)

modelX = modelQuad()
modelZ = modelLineaire()
modelA = modelLineaire()
listModel: list[Param] = [Param("x",modelX, data), Param("z", modelZ, data), Param("a", modelA, data)]
params = []
for model in listModel:
    params.extend(model.model.parameters())
opt = optim.Adam(params, lr=5e2)  #lr = learning rate
lastLoss = math.inf
i = 0
TARGETMAXLOSS = 10
while lastLoss > TARGETMAXLOSS:
    yPredict = 0
    for model in listModel:
        yPredict += model.model(model.tensorData)
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
        fig.suptitle(f"iter {i}, Loss = {loss.data}")
        plt.show()
