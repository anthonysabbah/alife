import os 
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)


import unittest
import torch
from geneutils import Genome
from brain import Brain 
from config import CONFIG

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
    int(CONFIG['MIN_CREATURE_SIZE'] + (SIZE/255) * (CONFIG['MAX_CREATURE_SIZE'] - CONFIG['MIN_CREATURE_SIZE']))
    )

    self.assertEqual(
      genes.energyCap, 
      CONFIG['MIN_ENERGY_CAP'] + (genes.size - CONFIG['MIN_CREATURE_SIZE']) * \
      (CONFIG['MAX_ENERGY_CAP'] - CONFIG['MIN_ENERGY_CAP']) / (CONFIG['MAX_CREATURE_SIZE'] - CONFIG['MIN_CREATURE_SIZE'])
    )

if __name__ == '__main__':
    unittest.main()