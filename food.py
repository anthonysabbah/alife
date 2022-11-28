from OpenGL import GLU # OpenGL Utility Library, extends OpenGL functionality
from OpenGL.arrays import vbo
import pygame, sys
from pygame.locals import *
from config import *
import random

class Food(pygame.sprite.Sprite):
  """
  ### Arguments:
  size: tuple[width: int, height: int] - size of food in world space
  coords: tuple[x: int, y: int] - x and y coords of food (centered) in world space
  energy: 
  """
  def __init__(self, size: tuple[int, int], coords: tuple[int, int], energy=0.5):
    super().__init__()
    self.energyLeft = energy
    self.size = int(energy * size[0]), int(energy * size[1]) # in world coords, NOT WINDOW COORDS
    self.image = pygame.Surface(self.size).convert_alpha()
    self.image.fill((255, 255, 0))
    self.rect = self.image.get_rect()
    self.rect.center = coords

  def draw(self, surface: pygame.Surface):
    surface.blit(self.image, self.rect)
