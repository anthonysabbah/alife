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
from geneutils import Genome, mutateGenome
from brain import Brain
from config import * 

random.seed(TORCH_SEED)
torch.manual_seed(TORCH_SEED)
np.random.seed(TORCH_SEED)

class World(object):
  def __init__(self, borderDims=list([int, int]), foodList=[], creatureList=[], foodPerTimestep: int = 0.5):
    # self.entities = []
    self.foodList = foodList
    self.creatureList = creatureList
    self.foodPerTimestep = foodPerTimestep 
    self.lastUpdateTime = time.time()
    self.borders = pygame.Rect(0, 0, borderDims[0], borderDims[1])
    self.creatureGen = 0
    self.maxFitness = -1
    self.foodToGive = foodPerTimestep
    self.timePassed = 0
    self.bestGenome = -1

    self.device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using {self.device} device")


  def update(self, surface: pygame.Surface):
      self.growFood()
      self.updateCreatures()
      self.drawAll(surface=surface)
      self.timePassed += 1

  def growFood(self):
    if len(self.foodList) < MAX_FOOD and (int(self.foodToGive) > 0):
      coords = (
        random.randint(FOODSIZE[0], WORLDSIZE[0] - FOODSIZE[0]), 
        random.randint(FOODSIZE[1], WORLDSIZE[1] - FOODSIZE[1])
      )
      self.foodList.append(Food(coords=coords, size=FOODSIZE))
      self.foodToGive -= self.foodToGive

    self.foodToGive += self.foodPerTimestep
    self.foodToGive = min(MAX_FOOD, self.foodToGive)

  def updateCreatures(self):
    if len(self.creatureList) < NUM_CREATURES:
      coords = (
        random.randint(FOODSIZE[0], WORLDSIZE[0] - FOODSIZE[0]), 
        random.randint(FOODSIZE[1], WORLDSIZE[1] - FOODSIZE[1])
      )
      newBrain = Brain().to(device=self.device)

      randomGenes = Genome(
        random.randint(1, 255), 
        random.randint(1, 255), 
        random.randint(1, 255), 
        newBrain.state_dict()
      )
      genes = randomGenes
      # mutate existing high fitness genes instead of randomly generating genes
      if(self.creatureGen >= NUM_CREATURES):
        for c in self.creatureList:
          if c.getFitness() > self.maxFitness:
            self.maxFitness = c.getFitness()
            self.bestGenome = c.genes

        genes = self.bestGenome
        if random.random() < 0.3:
          genes = randomGenes

      id = str(uuid.uuid4().hex)
      self.creatureList.append(Creature(genes=genes, coords=coords, id=id))
      self.creatureGen += 1
    
    oldCreatures = self.creatureList
    for c in oldCreatures:
      if (self.borders.contains(c.rect) and c.energyLeft >= c.energyLossRate):
        self.creatureList, self.foodList = c.update(oldCreatures, self.foodList, self.borders)
      else: 
        self.creatureList.remove(c)

  def drawAll(self, surface: pygame.Surface):
    # Draw world border
    self.borders = pygame.draw.rect(surface=surface, rect=self.borders, width=5, color=(0, 255, 255))

    for f in self.foodList:
      f.draw(surface)

    for c in self.creatureList:
      c.draw(surface)
    


