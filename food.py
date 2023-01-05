import pygame, sys
from pygame.locals import *
from config import *

class Food(pygame.sprite.Sprite):
  """
  ### Arguments:
  size: tuple[width: int, height: int] - size of food in world space
  coords: tuple[x: int, y: int] - x and y coords of food (centered) in world space
  energy: 
  """
  def __init__(self, coords, size=CONFIG['FOODSIZE'], energy=CONFIG['FOOD_ENERGY']):
    super().__init__()
    self.energyLeft = energy
    self.size = int(size[0]), int(size[1]) # in world coords, NOT WINDOW COORDS
    self.image = pygame.Surface(self.size).convert_alpha()
    self.color = (0, 255, 0)
    self.image.fill(self.color)
    self.rect = self.image.get_rect()
    self.rect.center = coords
    pygame.draw.rect(self.image, (255, 0, 0), rect=self.rect)

  def draw(self, surface: pygame.Surface):
    surface.blit(self.image, self.rect)
