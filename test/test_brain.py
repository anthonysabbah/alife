import os 
import sys
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to
# the sys.path.
sys.path.append(parent)

import unittest
from unittest.mock import MagicMock
import torch
from torch import nn
from brain import NegateLayer, Brain

# seed for testing
torch.manual_seed(42069)

class TestNegateLayer(unittest.TestCase):
  def test_init(self):
    negate = NegateLayer((10,))
    shape = negate.drop.size()
    self.assertEqual(shape, torch.Size([10]))
  
  def test_forward(self):
    negate = NegateLayer((10,))
    x = torch.ones((10,))
    out = negate.forward(x)
    expected = x * negate.drop
    torch.testing.assert_close(out, expected)

class TestBrain(unittest.TestCase):
  def test_init(self):
    brain = Brain()
    modelDict = brain.state_dict()
    self.assertEqual(len(modelDict.keys()), 3)
    self.assertEqual(modelDict['lin0.weight'].size(), torch.Size([20,10]))
    self.assertEqual(modelDict['cancel0.drop'].size(), torch.Size([20]))
    self.assertEqual(modelDict['lin1.weight'].size(), torch.Size([6,20]))

  # def test_forward(self):
  #   x = torch.rand([10])
  #   randState = torch.random.get_rng_state()
  #   y = nn.Linear(2*3 + 4, 20, bias=False)(x)
  #   # torch.nn.init.uniform_(self.lin0.weight, 0, 1)
  #   y = NegateLayer(shape=(20,))(y)
  #   y = nn.ReLU()(y)
  #   expected = nn.Linear(20,6, bias=False)(y)
    
  #   torch.random.set_rng_state(randState)
  #   brain = Brain()
  #   out = brain.forward(x)
  #   torch.testing.assert_close(out, expected)



if __name__ == '__main__':
    unittest.main()