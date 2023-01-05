import pickle
import torch
import numpy as np
from config import CONFIG

class Genome(object):
  # input params are all within [1, 255]
  def __init__(self, size: int, energyCap: int, mutationRate: int, neuronalConnections):
    self.size =  int(CONFIG['MIN_CREATURE_SIZE'] + \
      (size/255) * (CONFIG['MAX_CREATURE_SIZE'] - CONFIG['MIN_CREATURE_SIZE']))

    self.energyCap = CONFIG['MIN_ENERGY_CAP'] + (self.size - CONFIG['MIN_CREATURE_SIZE']) * \
    (CONFIG['MAX_ENERGY_CAP'] - CONFIG['MIN_ENERGY_CAP']) / (CONFIG['MAX_CREATURE_SIZE'] - CONFIG['MIN_CREATURE_SIZE'])

    self.mutationRate =  CONFIG['MIN_MUTATION_RATE'] + (size/255) * (CONFIG['MAX_MUTATION_RATE'] - CONFIG['MIN_MUTATION_RATE'])
    self.neuronalConnections = neuronalConnections  # pytorch model state_dict

  def encode(self):
    return pickle.dumps(self.__dict__)

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
  #TODO: is this good?
  if np.random.rand() < g.mutationRate:
    m = g.mutationRate
    size = g.size
    mutationRate = g.mutationRate
    connections = g.neuronalConnections
    energyCap = g.energyCap
    if(np.random.rand() < m):
      # mutate size and energy cap accordingly
      size = 255 * np.random.rand()
      energyCap = 255 * np.random.rand()

    if(np.random.rand() < m):
      # mutate mutation rate - omegalol
      mutationRate = 255 * np.random.rand()

    # mutate brain
    connections = g.neuronalConnections
    cancel0 = connections['cancel0.drop']
    lin0w = connections['lin0.weight']
    lin1w = connections['lin1.weight']

    cancel0Prob = torch.rand(cancel0.size())
    cancel0 = (cancel0Prob<m)

    for i in range(len(lin0w)):
      lin0w[i] = np.random.uniform(-1,1) if np.random.rand() < m else lin0w[i]

    for i in range(len(lin1w)):
      lin1w[i] = np.random.uniform(-1,1) if np.random.rand() < m else lin1w[i]

    connections['cancel0.drop'] = cancel0
    connections['lin0.weight'] = lin0w
    connections['lin1.weight'] = lin1w

    return Genome(size, mutationRate, energyCap, connections)
  return g