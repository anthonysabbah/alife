from config import *
import pickle
from brain import Brain
import torch
import random

class Genome(object):
  # input params are all within [1, 255]
  def __init__(self, size: int, energyCap: int, mutationRate: int, neuronalConnections):
    self.size =  int(MIN_CREATURE_SIZE + (size/255) * (MAX_CREATURE_SIZE - MIN_CREATURE_SIZE))

    self.energyCap = MIN_ENERGY_CAP + (self.size - MIN_CREATURE_SIZE) * \
    (MAX_ENERGY_CAP - MIN_ENERGY_CAP) / (MAX_CREATURE_SIZE - MIN_CREATURE_SIZE)

    self.mutationRate =  MIN_MUTATION_RATE + (size/255) * (MAX_MUTATION_RATE - MIN_MUTATION_RATE)
    self.neuronalConnections = neuronalConnections  # pytorch model state_dict

  def encode(self):
    return pickle.dumps(self)

  def __eq__(self, __o: object) -> bool:
    if isinstance(__o, Genome):
      if self.size != __o.size:
        return False
      if self.mutationRate != __o.mutationRate:
        return False
      if self.neuronalConnections != __o.neuronalConnections:
        return False
      return True

    return False
   

def mutateGenome(g: Genome) -> Genome:
  m = g.mutationRate
  size = g.size
  mutationRate = g.mutationRate
  connections = g.neuronalConnections
  energyCap = g.energyCap
  if(random.random() < m):
    # mutate size and energy cap accordingly
    size = 255 * random.random()
    energyCap = 255 * random.random()

  if(random.random() < m):
    # mutate mutation rate - omegalol
    mutationRate = 255 * random.random()

  connections = g.neuronalConnections
  cancel0 = connections['cancel0.drop']
  cancel1 = connections['cancel1.drop']
  for i in range(len(cancel0)):
    cancel0[i] = int(not(cancel0[i])) if random.random() < m else cancel0[i]
  for i in range(len(cancel1)):
    cancel1[i] = int(not(cancel1[i])) if random.random() < m else cancel1[i]

  connections['cancel0.drop'] = cancel0
  connections['cancel1.drop'] = cancel1

  return Genome(size, mutationRate, energyCap, connections)

  # for weight in neuronalConnection:

# test code
# from brain import Brain
# b = Brain()
# weights = b.state_dict()
# conn = {}
# conn['cancel0.drop'] = weights['cancel0.drop']
# conn['cancel1.drop'] = weights['cancel1.drop']
# print(conn)

# g = Genome(size=120, mutationRate=50, neuronalConnections=conn)
# newG = mutateGenome(g)
# print(newG.neuronalConnections)
  
