import torch
import numpy as np
import pygame

from geneutils import Genome
from brain import Brain
from creature import Creature
from food import Food
from world import World


def customEncoder(obj):
  if isinstance(obj, World):
    return obj.__dict__
  if isinstance(obj, torch.Tensor):
    return obj.cpu().detach().numpy()
  if isinstance(obj, pygame.Surface):
    return None
  if isinstance(obj, Brain):
    return obj.state_dict()
  if isinstance(obj, Genome):
    return obj.__dict__
  # get rid of non-critical info
  if isinstance(obj, Creature):
    enc = obj.__dict__.copy()
    enc.pop('energyBarBackground')
    enc.pop('energyBar')
    enc.pop('body')
    enc.pop('brain')
    enc.pop('genes')
    enc.pop('_Sprite__g')

    return enc
  if isinstance(obj, Food):
    return obj.__dict__
  if isinstance(obj, pygame.Vector2):
    return np.array(obj)
  if isinstance(obj, pygame.Rect):
    return np.array(obj)
    # return orjson.dumps(obj.state_dict(), option=orjson.OPT_SERIALIZE_NUMPY, default=customEncoder)