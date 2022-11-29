from config import *
import io

"""
Will use direct encoding for neuronal connections  in brain (weights)

The brains will have an architecture that is constant, and inference will be performed
with pytorch:

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
    self.cancel0 = NegateLayer(shape=(1,10))
    self.relu0 = nn.ReLU()
    self.cancel1 = NegateLayer(shape=(1,10))
    self.lin1 = nn.Linear(10, 4, bias=False)

  def forward(self, x):
    x = self.flatten(x)
    x = self.lin0(x)
    x = self.cancel0(x)
    x = self.relu0(x)
    x = self.cancel1(x)
    logits = self.lin1(x)
    return logits

params: 3060

"""
class Genome:
  def __init__(self, size: int, mutationRate: int, neuronalConnections):
    self.size =  MIN_CREATURE_SIZE + (size/255) * (MAX_CREATURE_SIZE - MIN_CREATURE_SIZE)
    self.mutationRate =  MIN_MUTATION_RATE + (size/255) * (MAX_MUTATION_RATE - MIN_MUTATION_RATE)
    self.neuronalConnections = neuronalConnections

  # def __repr__(self):
  #   return bin(self.size) + bin(self.mutationRate)[2:] + bin(self.neuronalConnections)[2:]