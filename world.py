import numpy as np
import pygame
import random
import OpenGL.GL as gl
from OpenGL import GLU # OpenGL Utility Library, extends OpenGL functionality
from OpenGL.arrays import vbo

from food import Food
from config import * 

class World(object):
  def __init__(self, foodList=[], creatureList=[]):
    # self.entities = []
    self.foodList = foodList
    self.creatureList = creatureList
    self.a = np.array([1,0])

  def update():
    pass

  def growFood(self, coords: tuple[int, int]):
    self.foodList.append(Food(coords=coords, size=FOODSIZE))

  def drawAll(self, surface: pygame.Surface):
    for f in self.foodList:
      f.draw(surface)