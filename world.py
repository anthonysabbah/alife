import numpy as np
import pygame
import torch

import uuid
from food import Food
from creature import Creature
from geneutils import Genome
from brain import Brain
from config import CONFIG


class World(object):
  def __init__(self, borderDims=list([int, int]), foodList=[], creatureList=[], foodPerTimestep: int = 0.5):
    # self.entities = []
    torch.manual_seed(CONFIG['TORCH_SEED'])
    np.random.seed(CONFIG['TORCH_SEED'])
    self.foodList = foodList
    self.creatureList = creatureList
    self.foodPerTimestep = foodPerTimestep 
    self.borders = pygame.Rect(0, 0, borderDims[0], borderDims[1])
    self.creatureGen = 0
    self.maxFitness = -1
    self.foodToGive = foodPerTimestep
    self.tick = 0
    self.bestGenome = None
    self.torchRNGState = torch.get_rng_state()
    self.npRNGState = np.random.get_state()

    self.device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using {self.device} device")


  def update(self, surface: pygame.Surface):
      self.growFood()
      self.updateCreatures()
      self.drawAll(surface=surface)
      self.torchRNGState = torch.get_rng_state()
      self.npRNGState = np.random.get_state()
      self.tick += 1

  def growFood(self):
    if len(self.foodList) < CONFIG['MAX_FOOD'] and (int(self.foodToGive) > 0):
      coords = (
        np.random.randint(CONFIG['FOODSIZE'][0], CONFIG['WORLDSIZE'][0] - CONFIG['FOODSIZE'][0]), 
        np.random.randint(CONFIG['FOODSIZE'][1], CONFIG['WORLDSIZE'][1] - CONFIG['FOODSIZE'][1]), 
      )

      self.foodList.append(Food(coords=coords))
      self.foodToGive -= self.foodToGive

    self.foodToGive += self.foodPerTimestep
    self.foodToGive = min(CONFIG['MAX_FOOD'], self.foodToGive)

  def updateCreatures(self):
    if len(self.creatureList) < CONFIG['NUM_CREATURES']:
      coords = (
        np.random.randint(CONFIG['FOODSIZE'][0], CONFIG['WORLDSIZE'][0] - CONFIG['FOODSIZE'][0]), 
        np.random.randint(CONFIG['FOODSIZE'][1], CONFIG['WORLDSIZE'][1] - CONFIG['FOODSIZE'][1]), 
      )

      newBrain = Brain()
      randomGenes = Genome(
        *np.random.randint(1, 255, size=(3,)),
        newBrain.state_dict()
      )

      genes = randomGenes
      # mutate existing high fitness genes instead of randomly generating genes
      if(self.creatureGen >= CONFIG['NUM_CREATURES']):
        for c in self.creatureList:
          if c.getFitness() > self.maxFitness:
            self.maxFitness = c.getFitness()
            self.bestGenome = c.genes

        genes = self.bestGenome
        if np.random.random() < 0.3:
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
    


