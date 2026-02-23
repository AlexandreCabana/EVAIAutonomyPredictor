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

class myDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)
    def __getitem__(self, idx):
        return self.data[idx]



class modelQuad(nn.Module):
    def __init__(self):
        super().__init__()
        # initialize all parameters that we will need
        self.weights1 = nn.Parameter(torch.randn(1, 1))
        self.weights2 = nn.Parameter(torch.randn(1, 1))
        self.bias3 = nn.Parameter(torch.zeros(1))
        self.sinOutMultipler = nn.Parameter(torch.randn(1, 1))
        self.sinInMultipler = nn.Parameter(torch.randn(1, 1))
        self.sinOffset = nn.Parameter(torch.randn(1, 1))

    def forward(self, xb):
        return (self.weights1 * (xb)**2 +
                self.weights2 * (xb) +
                self.sinOutMultipler*
                torch.sin(self.sinInMultipler*xb + self.sinOffset)*xb +
                self.bias3)
def mse(y, y_hat): return ((y - y_hat)**2).mean()

#generate dataset
data = pd.DataFrame(pd.Series(np.random.randint(-1000, 1000, size=200)),columns=['x'])
data["y"] = (random.randint(-50,50)*data["x"]**2 +
             random.randint(-50,50)*data["x"] +
             random.randint(-50,50) +
             random.randint(70000,80000)*
             np.sin(random.randint(-50,50)*data["x"] +
                      random.randint(-50,50))*data["x"]+
             np.random.randint(-500000,500000, size=len(data)))

x = torch.tensor(data["x"].values, dtype=torch.float32).view(-1, 1)
y = torch.tensor(data["y"].values, dtype=torch.float32).view(-1, 1)

model = modelQuad()
opt = optim.Adam(model.parameters(), lr = 5e2) #lr = learning rate
lastLoss = math.inf
i=0
data.sort_values('x', inplace=True)
while lastLoss > 10000000:
    y_hat = model(x)
    loss = mse(y, y_hat)
    loss.backward()
    opt.step()
    opt.zero_grad()
    i+=1
    if i%10000==0:
        lastLoss=loss.data
        print(f"iter {i}, Loss = {loss.data}")
        for name, param in model.named_parameters():
            if param.requires_grad:
                print(name, param.data.item())
        print()
        plt.plot(data["x"], data["y"], 'o')
        plt.plot(data["x"], list(model.named_parameters())[0][1].data.item()*data["x"]**2+
                 list(model.named_parameters())[1][1].data.item()*data["x"] +
                 list(model.named_parameters())[2][1].data.item()+(
                 list(model.named_parameters())[3][1].data.item()*
                 np.sin(list(model.named_parameters())[4][1].data.item()*data["x"]+list(model.named_parameters())[5][1].data.item())))

        plt.xlabel("x")
        plt.ylabel("y")
        plt.show()
