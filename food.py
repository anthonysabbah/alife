from OpenGL import GLU # OpenGL Utility Library, extends OpenGL functionality
from OpenGL.arrays import vbo
import pygame, sys
from pygame.locals import *
from config import *
import random

class Food(pygame.sprite.Sprite):
  def __init__(self):
    super().__init__()
    self.size = (10, 10) # in world coords, NOT WINDOW COORDS
    self.image = pygame.Surface(self.size).convert_alpha()
    self.image.fill((255, 255, 0))
    self.rect = self.image.get_rect()
    self.rect.center = (
      random.randint(self.rect[0], WORLDSIZE[0] - self.rect[0]), 
      random.randint(self.rect[1], WORLDSIZE[1] - self.rect[0])
    )

  def draw(self, surface: pygame.Surface):
    surface.blit(self.image, self.rect)
