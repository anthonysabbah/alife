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
    self.flatten = nn.Flatten(start_dim=0)
    self.lin0 = nn.Linear(3*10*10, 10, bias=False)
    self.cancel0 = NegateLayer(shape=(10,))
    self.relu0 = nn.ReLU()
    self.cancel1 = NegateLayer(shape=(10,))
    self.lin1 = nn.Linear(10, 4, bias=False)

  def forward(self, x):
    x = self.flatten(x)
    x = self.lin0(x)
    x = self.cancel0(x)
    x = self.relu0(x)
    x = self.cancel1(x)
    logits = self.lin1(x)
    return logits