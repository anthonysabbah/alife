from OpenGL import GLU # OpenGL Utility Library, extends OpenGL functionality
from OpenGL.arrays import vbo
import torch
import numpy as np
import pygame
from pygame.locals import *
import random

from geneutils import Genome
from brain import Brain
from food import Food
import cv2
from config import *
import time

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
    # pygame.draw.rect(surf, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image.get_size()),2)

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
    self.color = (255,0,0)
    # square view

    # rect of body surface in image surface coords
    self.bodyRectImage = self.body.get_rect()
    self.bodyRectImage.midbottom = (self.image.get_rect()).midbottom
    # TODO: add bodyRect world coords here later
    self.bodyRectWorld = self.body.get_rect()
    # self.bodyRectWorld.center = self.

    # transparent canvases
    self.image.set_colorkey((0, 0, 0))
    self.body.set_colorkey((0, 0, 0))

    self.imageWorldRect = self.image.get_rect()

    self.bodyRectWorld.center = coords
    self.imageWorldRect.midbottom = self.bodyRectWorld.midbottom

    self.angle = 0
    # TODO: dont hard-code this
    self.brain = Brain().to('cpu')
    self.brain.load_state_dict(self.genes.neuronalConnections)

    # to be initialized soon
    self.mouthRect = None
    self.bodyRectWorldp0 = self.bodyRectWorld.topleft 
    self.bodyRectWorldp1 = self.bodyRectWorld.topright 
    self.bodyRectWorldp2 = self.bodyRectWorld.bottomright 
    self.bodyRectWorldp3 = self.bodyRectWorld.bottomleft 

    self.leftAntennaStartInit = self.leftAntennaStart = pygame.math.Vector2(self.bodyRectWorldp0) + pygame.math.Vector2(int(self.genes.size/4), 0)
    self.leftAntennaEndInit = self.leftAntennaEnd = pygame.math.Vector2(self.bodyRectWorldp0) + pygame.math.Vector2(0, -self.genes.size)

    self.rightAntennaStartInit = self.rightAntennaStart = pygame.math.Vector2(self.bodyRectWorldp1) + pygame.math.Vector2(-int(self.genes.size/4), 0)
    self.rightAntennaEndInit =  self.rightAntennaEnd = pygame.math.Vector2(self.bodyRectWorldp1) + pygame.math.Vector2(0, -self.genes.size)

    self.leftColor = np.zeros(3) 
    self.rightColor = np.zeros(3)

    self.leftAntennaRadius = pygame.Rect(self.bodyRectWorld)
    self.rightAntennaRadius = pygame.Rect(self.bodyRectWorld)
    self.creatureSensorRadius = pygame.Rect(self.bodyRectWorld)
    self.rect = self.bodyRectWorld
    self.vel = [0,0]

    # self.viewCanvas = pygame.Surface((self.genes.size,)*2).convert_alpha()
    #TODO Make viewing distance dependent on genome?

  # passes sensory input into neural net and registers outputs accordingly
  def update(self, creatures, foods):
    objects = creatures + foods
    leftAntennaDetections = np.array([[0,0,0]])
    rightAntennaDetections = np.array([[0,0,0]])

    for item in objects:
      if self.leftAntennaRadius.contains(item.rect):
        d = pygame.Vector2(item.rect.center - self.leftAntennaEnd).magnitude()
        r = self.leftAntennaRadius.width
        scaling = (r-d)/r
        leftAntennaDetections = np.append(
          leftAntennaDetections, 
          np.dot(scaling, np.asarray(item.color).reshape(1,3)), 
          axis=0
        )

      if self.rightAntennaRadius.contains(item.rect):
        d = pygame.Vector2(item.rect.center - self.rightAntennaEnd).magnitude()
        r = self.rightAntennaRadius.width
        scaling = (r-d)/r
        rightAntennaDetections = np.append(
          rightAntennaDetections, 
          np.dot(scaling, 
          np.asarray(item.color).reshape(1,3)), 
          axis=0
        )
        # print(rightAntennaDetections, 'R')

      foodScalar = 0
      if self.creatureSensorRadius.contains(item.rect) and isinstance(item, Food):
        d = (pygame.Vector2(item.rect.center) - pygame.Vector2(self.rect.center)).magnitude()
        r = self.rightAntennaRadius.width
        foodScalar = (r-d)/r if r != 0 else 1

    # apply sensor detected colors
    leftLen = len(leftAntennaDetections) - 1
    rightLen = len(leftAntennaDetections) - 1
    self.leftColor = (np.sum(leftAntennaDetections, axis=0)/leftLen)
    self.leftColor = np.zeros(3) if np.isnan(self.leftColor).any() else self.leftColor/255
    self.rightColor = (np.mean(rightAntennaDetections, axis=0)/rightLen)
    self.rightColor = np.zeros(3) if np.isnan(self.rightColor).any() else self.rightColor/255

    inputs = np.append(self.leftColor, self.rightColor)
    inputs = np.append(inputs, foodScalar)
    inputs = np.append(inputs, self.angle)
    inputs = np.append(inputs, np.random.random())
    inputs = torch.Tensor(inputs)
    outs = self.brain(inputs).detach().numpy()

    print('ins: ', inputs)
    print('outs: ', outs)

    vecOffset = (np.array(self.bodyRectWorldp1) - np.array(self.bodyRectWorldp0))/2
    top = np.array(self.bodyRectWorldp0) + vecOffset
    bottom = np.array(self.bodyRectWorldp3) + vecOffset
    dirVec = (top - bottom)/np.linalg.norm(top - bottom)
    vel = 5 * outs[0] * dirVec
    print("vel: ", vel)
    self.vel = np.asarray(vel, dtype=int)
    dTheta = int(10 * outs[1])

    self.move(self.vel[0], self.vel[1])
    self.rotate(2 * dTheta)
    self.color = (255, int(np.abs(outs[2]) * 255), int(np.abs(outs[2]) * 255))
    print("color: ", self.color)

    self.rotate(0)



  def move(self, dx, dy):
    self.bodyRectWorld.center = pygame.math.Vector2(self.bodyRectWorld.center) + pygame.math.Vector2(dx, dy)

    self.leftAntennaStartInit = self.leftAntennaStartInit + pygame.math.Vector2(dx, dy)
    self.leftAntennaEndInit = self.leftAntennaEndInit + pygame.math.Vector2(dx, dy)
    self.rightAntennaStartInit = self.rightAntennaStartInit + pygame.math.Vector2(dx, dy)
    self.rightAntennaEndInit = self.rightAntennaEndInit + pygame.math.Vector2(dx, dy)

    # self.leftAntennaStart  = self.leftAntennaStartInit
    # self.leftAntennaEnd    = self.leftAntennaEndInit
    # self.rightAntennaStart = self.rightAntennaStartInit
    # self.rightAntennaEnd   = self.rightAntennaEndInit

    self.bodyRectWorldp0 = self.bodyRectWorldp0 + pygame.math.Vector2(dx, dy)
    self.bodyRectWorldp1 = self.bodyRectWorldp1 + pygame.math.Vector2(dx, dy)
    self.bodyRectWorldp2 = self.bodyRectWorldp2 + pygame.math.Vector2(dx, dy)
    self.bodyRectWorldp3 = self.bodyRectWorldp3 + pygame.math.Vector2(dx, dy)


  def rotate(self, dTheta):
    self.angle += dTheta
    self.angle = self.angle % 360

    pivot = pygame.math.Vector2(self.bodyRectWorld.center)

    self.leftAntennaStart = (self.leftAntennaStartInit - pivot).rotate(-self.angle) + pivot
    self.leftAntennaEnd = (self.leftAntennaEndInit - pivot).rotate(-self.angle) + pivot

    self.rightAntennaStart = (self.rightAntennaStartInit - pivot).rotate(-self.angle) + pivot
    self.rightAntennaEnd = (self.rightAntennaEndInit - pivot).rotate(-self.angle) + pivot

    self.bodyRectWorldp0 = (pygame.math.Vector2(self.bodyRectWorld.topleft) - pivot).rotate(-self.angle) + pivot 
    self.bodyRectWorldp1 = (pygame.math.Vector2(self.bodyRectWorld.topright) - pivot).rotate(-self.angle) + pivot 
    self.bodyRectWorldp2 = (pygame.math.Vector2(self.bodyRectWorld.bottomright) - pivot).rotate(-self.angle) + pivot 
    self.bodyRectWorldp3 = (pygame.math.Vector2(self.bodyRectWorld.bottomleft) - pivot).rotate(-self.angle) + pivot 

  def draw(self, surface: pygame.Surface):
    w, h = self.body.get_size()

    pygame.draw.ellipse(
      self.body, 
      self.color,
      self.body.get_rect()
    )

    pygame.draw.ellipse(
      self.body, 
      (0,0,255), 
      self.body.get_rect(),
      3
    )

    self.creatureSensorRadius = pygame.draw.circle(
      surface=surface, 
      color=pygame.Color(255,255,255), 
      center=self.bodyRectWorld.center,
      radius=self.body.get_width() * 3,
      width=1,
    )

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
    self.rect = pygame.draw.lines(
      surface=surface, 
      color=(255, 0, 0), 
      closed=True, 
      points=[self.bodyRectWorldp0, self.bodyRectWorldp1, self.bodyRectWorldp2, self.bodyRectWorldp3], 
      width=1
    )

    
    self.leftAntenna = pygame.draw.line(
      surface=surface,
      color=(255,255,255),
      start_pos=self.leftAntennaStart,
      end_pos=self.leftAntennaEnd,
      width=1
    )

    self.rightAntenna = pygame.draw.line(
      surface=surface,
      color=(255,255,255),
      start_pos=self.rightAntennaStart,
      end_pos=self.rightAntennaEnd,
      width=1
    )
    
    self.leftAntennaRadius = pygame.draw.circle(
      surface=surface, 
      color=pygame.Color(255,255,255), 
      center=self.leftAntennaEnd,
      radius=self.body.get_width(),
      width=1,
    )

    self.rightAntennaRadius = pygame.draw.circle(
      surface=surface, 
      color=pygame.Color(255,255,255), 
      center=self.rightAntennaEnd,
      radius=self.body.get_width(),
      width=1,
    )

    self.velLine = pygame.draw.line(
      surface=surface,
      color=pygame.Color(0,255,0),
      start_pos=self.bodyRectWorld.center,
      end_pos=np.array(self.bodyRectWorld.center) + 5 * self.vel,
      width = 2
    )