import os 
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


import unittest
import torch
from geneutils import Genome
from brain import Brain 
from config import *

SIZE = 120
ENERGY_CAP = 120
MUTATION_RATE = 20


class TestGenome(unittest.TestCase):
  def test_init(self):
    weights = torch.load('test/testModel.pt')
    # not rlly needed with current model, but just in case
    genes = Genome(
      size=SIZE, 
      energyCap=ENERGY_CAP, 
      mutationRate=MUTATION_RATE,
      neuronalConnections=weights
    )

    self.assertEqual(genes.size, 
    int(MIN_CREATURE_SIZE + (SIZE/255) * (MAX_CREATURE_SIZE - MIN_CREATURE_SIZE))
    )

    self.assertEqual(
      genes.energyCap, 
      MIN_ENERGY_CAP + (genes.size - MIN_CREATURE_SIZE) * \
      (MAX_ENERGY_CAP - MIN_ENERGY_CAP) / (MAX_CREATURE_SIZE - MIN_CREATURE_SIZE)
    )

if __name__ == '__main__':
    unittest.main()