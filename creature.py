from OpenGL import GLU # OpenGL Utility Library, extends OpenGL functionality
from OpenGL.arrays import vbo
import pygame, sys
from pygame.locals import *
from config import *
import random

class Creature(pygame.sprite.Sprite):
  def __init__(
    self, 
    size: tuple[int, int] = (20, 20), 
    coords: tuple[int, int] = (0, 0)
  ):

    self.size = size
    self.image = pygame.Surface(self.size).convert_alpha()
    self.image.set_colorkey((0, 0, 0))
    self.rect = self.image.get_rect()
    self.rect.center = coords

  def draw(self, surface: pygame.Surface):
    pygame.draw.ellipse(
      self.image, 
      (255, 0, 0),
      self.image.get_rect()
    )

    pygame.draw.ellipse(
      self.image, 
      (0,0,255), 
      self.image.get_rect(),
      3
    )

    surface.blit(self.image, self.rect)