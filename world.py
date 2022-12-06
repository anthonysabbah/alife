import numpy as np
import pygame
import random
import OpenGL.GL as gl
import time
import torch
from OpenGL import GLU # OpenGL Utility Library, extends OpenGL functionality
from OpenGL.arrays import vbo

import uuid
from food import Food
from creature import Creature
from geneutils import Genome
from brain import Brain
from config import * 

class World(object):
  def __init__(self, borderDims=list([int, int]), foodList=[], creatureList=[], foodPerSecond: int = 1):
    # self.entities = []
    self.foodList = foodList
    self.creatureList = creatureList
    self.foodPerSecond = foodPerSecond 
    self.lastUpdateTime = time.time()
    self.borders = pygame.Rect(0, 0, borderDims[0], borderDims[1])

    torch.manual_seed(TORCH_SEED)
    self.device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using {self.device} device")


  def update(self, surface: pygame.Surface):
      self.growFood()
      self.updateCreatures()
      self.drawAll(surface=surface)

  def growFood(self):
    t = time.time()
    if t - self.lastUpdateTime > 1:
      for i in range(self.foodPerSecond):
        coords = (
          random.randint(FOODSIZE[0], WORLDSIZE[0] - FOODSIZE[0]), 
          random.randint(FOODSIZE[1], WORLDSIZE[1] - FOODSIZE[1])
        )
        self.foodList.append(Food(coords=coords, size=FOODSIZE))
      self.lastUpdateTime = t 

  def updateCreatures(self):
    self.randomGen = 0
    if len(self.creatureList) < NUM_CREATURES:
      coords = (
        random.randint(FOODSIZE[0], WORLDSIZE[0] - FOODSIZE[0]), 
        random.randint(FOODSIZE[1], WORLDSIZE[1] - FOODSIZE[1])
      )
      newBrain = Brain().to(device=self.device)

      genes = Genome(
        random.randint(1, 255), 
        random.randint(1, 255), 
        random.randint(1, 255), 
        newBrain.state_dict()
      )
      # mutate existing high fitness genes instead of randomly generating genes
      # if(self.randomGen >= NUM_CREATURES):
      #   genes = mutateGenes

      id = str(uuid.uuid4().hex)
      self.creatureList.append(Creature(genes=genes, coords=coords, id=id))
    
    for c in self.creatureList:
      if (self.borders.contains(c.rect) and c.energyLeft >= c.energyLossRate):
        c.update(self.creatureList, self.foodList)
      else: 
        self.creatureList.remove(c)

  def drawAll(self, surface: pygame.Surface):
    # Draw world border
    self.borders = pygame.draw.rect(surface=surface, rect=self.borders, width=5, color=(0, 255, 255))

    for f in self.foodList:
      f.draw(surface)

    for c in self.creatureList:
      c.draw(surface)