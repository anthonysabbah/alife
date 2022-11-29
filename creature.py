from OpenGL import GLU # OpenGL Utility Library, extends OpenGL functionality
from OpenGL.arrays import vbo
import torch
import numpy as np
import pygame
from pygame.locals import *
import random

from geneutils import Genome
from brain import Brain
import cv2
from config import *

def blitRotate(surf, image, pos, originPos, angle):

    # offset from pivot to center
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    
    # roatated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # roatetd image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

    # rotate and blit the image
    surf.blit(rotated_image, rotated_image_rect)
  
    # draw rectangle around the image
    pygame.draw.rect(surf, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image.get_size()),2)

def blitRotate2(surf, image, topleft, angle):

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)
    # pygame.draw.rect(surf, (255, 0, 0), new_rect, 2)

def rot_center(image, angle):
  """rotate an image while keeping its center and size"""
  orig_rect = image.get_rect()
  rot_image = pygame.transform.rotate(image, angle)
  rot_rect = orig_rect.copy()
  rot_rect.center = rot_image.get_rect().center
  rot_image = rot_image.subsurface(rot_rect).copy()
  return rot_image


class Creature(pygame.sprite.Sprite):
  def __init__(
    self,
    genes: Genome ,
    coords: tuple([int, int]) = (0, 0),
    brain: Brain = Brain()
  ):
    self.genes = genes

    width = self.genes.size 
    if self.genes.size < MAX_CREATURE_VIEW_DIST:
      width = MAX_CREATURE_VIEW_DIST

    dims = (width, self.genes.size + MAX_CREATURE_VIEW_DIST)

    self.image = pygame.Surface(dims)
    self.body = pygame.Surface((self.genes.size,)*2)
    # square view

    # rect of body surface in image surface coords
    self.bodyRectImage = self.body.get_rect()
    self.bodyRectImage.midbottom = (self.image.get_rect()).midbottom
    # TODO: add bodyRect world coords here later
    self.bodyRectWorld = self.body.get_rect()
    # self.bodyRectWorld.center = self.

    self.viewRect = pygame.Rect((0,0), (MAX_CREATURE_VIEW_DIST,)*2)
    self.viewRectImage = self.viewRect
    self.viewRectImage.midbottom = self.bodyRectImage.midtop
    self.viewRectWorld = self.viewRect

    # transparent canvases
    self.image.set_colorkey((0, 0, 0))
    self.body.set_colorkey((0, 0, 0))

    self.imageWorldRect = self.image.get_rect()

    self.bodyRectWorld.center = coords
    self.imageWorldRect.midbottom = self.bodyRectWorld.midbottom
    self.viewRectWorld.midbottom = self.bodyRectWorld.midtop

    self.angle = 0
    # TODO: dont hard-code this
    self.brain = Brain().to('cpu')
    self.brain.load_state_dict(self.genes.neuronalConnections)
    self.mouthRect = None

    # self.viewCanvas = pygame.Surface((self.genes.size,)*2).convert_alpha()
    #TODO Make viewing distance dependent on genome?
  def update(self):
    # pygame.draw.line() 
    moveX = random.randint(-5, 5)
    moveY = random.randint(-5, 5)

    self.angle += 1
    self.angle = self.angle % 360

    # self.imageWorldRect = self.imageWorldRect.move(moveX, moveY)
    # # we can be lazy with the body rect - they're square so no need to rotate them lmao.
    # self.bodyRectWorld = self.bodyRectWorld.move(moveX, moveY)
    pivot = pygame.math.Vector2(self.bodyRectWorld.center)

    self.bodyRectWorldp0 = (pygame.math.Vector2(self.bodyRectWorld.topleft) - pivot).rotate(-self.angle) + pivot 
    self.bodyRectWorldp1 = (pygame.math.Vector2(self.bodyRectWorld.topright) - pivot).rotate(-self.angle) + pivot 
    self.bodyRectWorldp2 = (pygame.math.Vector2(self.bodyRectWorld.bottomright) - pivot).rotate(-self.angle) + pivot 
    self.bodyRectWorldp3 = (pygame.math.Vector2(self.bodyRectWorld.bottomleft) - pivot).rotate(-self.angle) + pivot 

    self.viewRectWorldp0 = (pygame.math.Vector2(self.viewRectWorld.topleft) - pivot).rotate(-self.angle) + pivot 
    self.viewRectWorldp1 = (pygame.math.Vector2(self.viewRectWorld.topright) - pivot).rotate(-self.angle) + pivot 
    self.viewRectWorldp2 = (pygame.math.Vector2(self.viewRectWorld.bottomright) - pivot).rotate(-self.angle) + pivot 
    self.viewRectWorldp3 = (pygame.math.Vector2(self.viewRectWorld.bottomleft) - pivot).rotate(-self.angle) + pivot 


    # self.viewRectWorld = self.viewRect.move(moveX, moveY)

  def draw(self, surface: pygame.Surface):
    w, h = self.body.get_size()

    pygame.draw.ellipse(
      self.body, 
      (255, 0, 0),
      self.body.get_rect()
    )

    pygame.draw.ellipse(
      self.body, 
      (0,0,255), 
      self.body.get_rect(),
      3
    )

    pygame.draw.rect(
      self.image, 
      (125, 0, 125),
      self.image.get_rect(),
      width = 1
    )

    # pygame.draw.rect(
    #   self.image, 
    #   (0, 255, 0),
    #   self.viewRect,
    #   width = 1
    # )

    self.mouthRectWorld = pygame.draw.line(
      self.body,
      (0,0,0,0),
      (int(w/2), int(h/2)),
      (int(w/2), 0),
      width = int(w/5)
    )

    # self.mouthRect.midbottom = self.bodyRect.center

    self.image.blit(self.body, self.bodyRectImage)

    blitRotate(
      surface, 
      self.image, 
      self.bodyRectWorld.center,
      self.bodyRectImage.center,
      self.angle
    )

    # pygame.draw.rect(surface=surface, rect=self.bodyRectWorld, color=(0,255,255), width=1)
    self.bodyRectBox = pygame.draw.lines(
      surface=surface, 
      color=(255, 255, 0), 
      closed=True, 
      points=[self.bodyRectWorldp0, self.bodyRectWorldp1, self.bodyRectWorldp2, self.bodyRectWorldp3], 
      width=1
    )


    self.viewRectBox = pygame.draw.lines(
      surface=surface, 
      color=(0, 255, 0), 
      closed=True, 
      points=[self.viewRectWorldp0, self.viewRectWorldp1, self.viewRectWorldp2, self.viewRectWorldp3], 
      width=1
    )

    print(self.viewRectBox)
    # self.tempVision = pygame.Surface((self.viewRectBox.width, self.viewRectBox.height))
    self.vision = pygame.Surface((self.viewRectBox.width, self.viewRectBox.height))
    self.tempVision = self.vision

    self.tempVision.blit(surface, (0,0), area=self.viewRectBox)
    blitRotate(self.vision, self.tempVision, (0,0), self.viewRectBox.center, -self.angle)

    pygame.draw.rect(
      self.vision,
      (255,255,0),
      rect=self.tempVision.get_rect(),
      width=1
    )

    surface.blit(self.vision, (100,100))

    # self.vision.blit(sub, (0,0))
    self.visionArray = pygame.surfarray.pixels3d(self.vision) 
    # cv2.imshow('vision', self.visionArray)
    # cv2.waitKey(-1)


    # surface.blit(self.image, self.imageWorldRect)