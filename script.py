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

    def __str__(self):
        return f"linear function with a: {self.weights.item()}, b: {self.bias.item()}"


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

    def __str__(self):
        return f"{self.letter} with {self.model}"

def normalized(x, mean, std):
    return (x - mean) / std


#generate dataset
NUMBEROFPOINTFORAI = 1000
data = pd.read_csv("DB/Kagle/EV_Energy_Consumption_Dataset.csv")
data["consumption_KWH_per_KM"] = data["Energy_Consumption_kWh"]/data["Distance_Travelled_km"]
comparedColumn = data["consumption_KWH_per_KM"]

y = torch.tensor(comparedColumn.values, dtype=torch.float32).view(-1, 1)

listModel: list[Param] = [Param("Speed_kmh",modelQuad(), data),
                          Param("Acceleration_ms2", modelLineaire(), data),
                          Param("Slope_%", modelCube(), data),
                          Param("Temperature_C",modelQuad(), data)]
numberOfColumnForGraph = len(listModel)//NUMBEROFGRAPHPERROW + (len(listModel)%NUMBEROFGRAPHPERROW >0)
params = []
for model in listModel:
    params.extend(model.model.parameters())
opt = optim.Adam(params, lr=0.00005)  #lr = learning rate
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

        for model in listModel:
            print(model)
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
            createFig(fig, model.lineSpace, yPredBaseOnModel, model.pandasData.values,
                      (comparedColumn-excludeData).values,
                      model.letter, NUMBEROFGRAPHPERROW ,numberOfColumnForGraph, index)
        fig.suptitle(f"iter {i}, Loss = {loss.data}, elapseTime = {round(time.time()-startTime)}")
        plt.legend()
        plt.show()
        if len(iteration)>=3:
            plotEvolution(iteration, lossHistory)

