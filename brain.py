import torch
from torch import nn
import numpy as np
import time

# sets default type
torch.set_default_dtype(torch.float32)

# Get cpu or gpu device for training.
# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"Using {device} device")

class NegateLayer(nn.Module):
  def __init__(self, shape):
    super().__init__()
    self.drop = torch.nn.Parameter(torch.randint(high=2, size=shape), requires_grad=False)

  def forward(self, x):
    return x * self.drop

# Define model
class Brain(nn.Module):
  def __init__(self):
    super().__init__()
    '''
    Inputs: [R_l, G_l, B_l, R_r, G_r, B_r, F, Energy, Angle, Cr]
    Outputs: [Vec, dAngle, Brightness, Eat, #Mate]
    '''

    self.lin0 = nn.Linear(2*3 + 4, 20)
    # torch.nn.init.uniform_(self.lin0.weight, 0, 1)
    self.cancel0 = NegateLayer(shape=(20,))
    self.relu0 = nn.ReLU()
    self.cancel1 = NegateLayer(shape=(20,))
    self.lin1 = nn.Linear(20, 4)
    # torch.nn.init.uniform_(self.lin0.weight, 0, 1)

  def forward(self, x):
    x = self.lin0(x)
    x = self.cancel0(x)
    x = self.relu0(x)
    x = self.cancel1(x)
    x = self.lin1(x)
    ones = torch.ones(len(x))
    logits = (x + ones)/(2 * ones)
    return logits