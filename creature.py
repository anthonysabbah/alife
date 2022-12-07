from OpenGL import GLU # OpenGL Utility Library, extends OpenGL functionality
from OpenGL.arrays import vbo
import torch
import numpy as np
import pygame
from pygame.locals import *
import random
import hashlib
import uuid

from geneutils import Genome, mutateGenome
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
    id,
    genes: Genome ,
    coords: tuple([int, int]) = (0, 0),
    brain: Brain = Brain()
  ):
    self.id=id
    self.genes = genes
    self.age = 0
    self.babiesMade = 0

    width = self.genes.size 
    if self.genes.size < MAX_CREATURE_VIEW_DIST:
      width = MAX_CREATURE_VIEW_DIST
    
    # color representing genome
    self.genecolor = '#' + (hashlib.sha256(self.genes.encode()).digest()).hex()[:6]
    
    self.energyLeft = self.genes.energyCap
    self.energyConsumed = 0

    self.energyLossRate = MIN_ENERGY_LOSS_RATE + \
    (MAX_ENERGY_LOSS_RATE - MIN_ENERGY_LOSS_RATE) * \
    (self.genes.size - MIN_CREATURE_SIZE)/ \
    (MAX_CREATURE_SIZE - MIN_CREATURE_SIZE)

    dims = (width, self.genes.size + MAX_CREATURE_VIEW_DIST)

    self.image = pygame.Surface(dims)
    self.body = pygame.Surface((self.genes.size,)*2)
    self.color = (255,0,0)
    # square view

    # rect of body surface in image surface coords
    self.bodyRectImage = self.body.get_rect()
    self.bodyRectImage.midbottom = (self.image.get_rect()).midbottom
    # TODO: add bodyRect world coords here later
    self.rect = self.body.get_rect()
    # self.rect.center = self.

    # transparent canvases
    self.image.set_colorkey((0, 0, 0))
    self.body.set_colorkey((0, 0, 0))

    self.imageWorldRect = self.image.get_rect()

    self.rect.center = coords
    self.imageWorldRect.midbottom = self.rect.midbottom

    self.angle = 0
    # TODO: dont hard-code this
    self.brain = Brain().to('cpu')
    self.brain.load_state_dict(self.genes.neuronalConnections)
    self.brain.eval()

    # to be initialized soon
    self.mouthRect = None
    self.rectp0 = self.rect.topleft 
    self.rectp1 = self.rect.topright 
    self.rectp2 = self.rect.bottomright 
    self.rectp3 = self.rect.bottomleft 

    self.leftAntennaStartInit = self.leftAntennaStart = pygame.math.Vector2(self.rectp0) + pygame.math.Vector2(int(self.genes.size/4), 0)
    self.leftAntennaEndInit = self.leftAntennaEnd = pygame.math.Vector2(self.rectp0) + pygame.math.Vector2(0, -self.genes.size)

    self.rightAntennaStartInit = self.rightAntennaStart = pygame.math.Vector2(self.rectp1) + pygame.math.Vector2(-int(self.genes.size/4), 0)
    self.rightAntennaEndInit =  self.rightAntennaEnd = pygame.math.Vector2(self.rectp1) + pygame.math.Vector2(0, -self.genes.size)

    self.leftColor = np.zeros(3) 
    self.rightColor = np.zeros(3)

    self.leftAntennaRadius = pygame.Rect(self.rect)
    self.rightAntennaRadius = pygame.Rect(self.rect)
    self.creatureSensorRadius = pygame.Rect(self.rect)
    self.rect = self.rect
    self.vel = [0,0]

    # self.viewCanvas = pygame.Surface((self.genes.size,)*2).convert_alpha()
    #TODO Make viewing distance dependent on genome?

  # passes sensory input into neural net and registers outputs accordingly
  def update(self, creatures, foods, worldBorder):
    self.energyLeft -= self.energyLossRate
    # print("energy left: ", self.energyLeft)
    if self.energyLeft < 0:
      #TODO: is this ok?
      return 

    objects = creatures + foods
    leftAntennaDetections = np.array([[0,0,0]])
    rightAntennaDetections = np.array([[0,0,0]])
    foodScalar = 0
    creatureScalar = 0

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

      foodNum = 0
      creatureNum = 0
      if self.creatureSensorRadius.contains(item.rect):
        d = (pygame.Vector2(item.rect.center) - pygame.Vector2(self.rect.center)).magnitude()
        r = self.creatureSensorRadius.width
        if isinstance(item, Food):
          foodNum += 1
          foodScalar += (r-d)/r 
        elif isinstance(item, Creature):
          creatureNum += 1
          creatureScalar += (r-d)/r 

    foodScalar = foodScalar/foodNum if foodNum > 0 else foodScalar
    creatureScalar = creatureScalar/creatureNum if creatureNum > 0 else creatureScalar

    # apply sensor detected colors
    # remove extra + this creature from the list length
    leftLen = len(leftAntennaDetections) - 1
    rightLen = len(leftAntennaDetections) - 1
    # print(leftAntennaDetections)
    # print(rightAntennaDetections)

    worldCenter = worldBorder.center

    worldBorderColor = np.array([0,255,255])

    leftVec = np.array(worldCenter) - np.array(self.leftAntennaEnd)
    rightVec = np.array(worldCenter) - np.array(self.rightAntennaEnd)
    leftColorOffset = (np.linalg.norm(leftVec)/np.sqrt(worldBorder.width**2))*worldBorderColor - np.array(self.color)
    rightColorOffset = (np.linalg.norm(rightVec)/np.sqrt(worldBorder.width**2))*worldBorderColor - np.array(self.color)

    self.leftColor = ((np.sum(leftAntennaDetections, axis=0) + leftColorOffset)/leftLen)
    self.leftColor = np.zeros(3) if np.isnan(self.leftColor).any() else self.leftColor/255
    self.rightColor = ((np.sum(rightAntennaDetections, axis=0) + rightColorOffset)/rightLen)
    self.rightColor = np.zeros(3) if np.isnan(self.rightColor).any() else self.rightColor/255

    inputs = np.append(self.leftColor, self.rightColor)
    inputs = np.append(inputs, foodScalar)
    inputs = np.append(inputs, self.energyLeft/self.genes.energyCap)
    inputs = np.append(inputs, self.angle/360)
    inputs = np.append(inputs, creatureScalar)
    # inputs = np.append(inputs, np.random.random())
    inputs = torch.Tensor(inputs)
    outs = self.brain(inputs).detach().numpy()

    # print('ins: ', inputs)
    # Outputs: [Vec, dAngle, Brightness, Eat]
    # print('outs: ', outs)

    #TODO: eats food for now, but should be able to eat creatures as well
    if outs[3] > 0.5:
      foods = self.eat(foods)

    if outs[4] > 0.9:
      creatures = self.reproduce(creatures)

    vecOffset = (np.array(self.rectp1) - np.array(self.rectp0))/2
    top = np.array(self.rectp0) + vecOffset
    bottom = np.array(self.rectp3) + vecOffset
    dirVec = (top - bottom)/np.linalg.norm(top - bottom)
    vel = MAX_SPEED * outs[0] * dirVec
    # print("vel: ", vel)
    self.vel = np.asarray(vel, dtype=int)
    dTheta = int(MAX_ANGLE_RATE * outs[1] * (-1 if outs[1] < 0.5 else 1))

    self.move(self.vel[0], self.vel[1])
    self.rotate(dTheta)
    # TODO: this is hacky, fix later plz
    self.color = (255, min(int(outs[2] * 255), 255), min(int(outs[2] * 255), 255))
    # print("color: ", self.color)

    self.age += 1

    return creatures, foods

  def move(self, dx, dy):
    self.rect.center = pygame.math.Vector2(self.rect.center) + pygame.math.Vector2(dx, dy)

    self.leftAntennaStartInit = self.leftAntennaStartInit + pygame.math.Vector2(dx, dy)
    self.leftAntennaEndInit = self.leftAntennaEndInit + pygame.math.Vector2(dx, dy)
    self.rightAntennaStartInit = self.rightAntennaStartInit + pygame.math.Vector2(dx, dy)
    self.rightAntennaEndInit = self.rightAntennaEndInit + pygame.math.Vector2(dx, dy)

    # self.leftAntennaStart  = self.leftAntennaStartInit
    # self.leftAntennaEnd    = self.leftAntennaEndInit
    # self.rightAntennaStart = self.rightAntennaStartInit
    # self.rightAntennaEnd   = self.rightAntennaEndInit

    self.rectp0 = self.rectp0 + pygame.math.Vector2(dx, dy)
    self.rectp1 = self.rectp1 + pygame.math.Vector2(dx, dy)
    self.rectp2 = self.rectp2 + pygame.math.Vector2(dx, dy)
    self.rectp3 = self.rectp3 + pygame.math.Vector2(dx, dy)

  def rotate(self, dTheta):
    self.angle += dTheta
    self.angle = self.angle % 360

    pivot = pygame.math.Vector2(self.rect.center)

    self.leftAntennaStart = (self.leftAntennaStartInit - pivot).rotate(-self.angle) + pivot
    self.leftAntennaEnd = (self.leftAntennaEndInit - pivot).rotate(-self.angle) + pivot

    self.rightAntennaStart = (self.rightAntennaStartInit - pivot).rotate(-self.angle) + pivot
    self.rightAntennaEnd = (self.rightAntennaEndInit - pivot).rotate(-self.angle) + pivot

    self.rectp0 = (pygame.math.Vector2(self.rect.topleft) - pivot).rotate(-self.angle) + pivot 
    self.rectp1 = (pygame.math.Vector2(self.rect.topright) - pivot).rotate(-self.angle) + pivot 
    self.rectp2 = (pygame.math.Vector2(self.rect.bottomright) - pivot).rotate(-self.angle) + pivot 
    self.rectp3 = (pygame.math.Vector2(self.rect.bottomleft) - pivot).rotate(-self.angle) + pivot 

  def eat(self, foods):
    #TODO: surely there's a more efficient way to do this right? Suuurrellyy....
    i = 0
    while i < len(foods):
      #TODO: can only eat a single piece in one go for now
      if self.rect.colliderect(foods[i].rect):
        self.energyLeft += foods[i].energyLeft
        if self.energyLeft > self.genes.energyCap:
          self.energyLeft = self.genes.energyCap

        self.energyConsumed += foods[i].energyLeft
        foods.pop(i)
      i += 1

    return foods

  def reproduce(self, creatures):
    cost = int(self.genes.energyCap/2)
    if self.energyLeft > cost:
      id = str(uuid.uuid4().hex)
      genes = mutateGenome(self.genes)
      coords = self.rect.center
      child = Creature(id=id, genes=genes, coords=coords)
      creatures.append(child)
      self.energyLeft -= cost
      self.energyLeft = min(0, self.energyLeft)
      self.babiesMade += 1
    return creatures

  # returns fitness function of the 
  def getFitness(self):
    # let this be the fitness function for now
    return 0.85 * self.energyConsumed + 0.1 * self.babiesMade +  0.005 * self.age

  def draw(self, surface: pygame.Surface):
    w, h = self.body.get_size()

    try:
      pygame.draw.ellipse(
        surface=self.body, 
        color=self.color,
        rect=self.body.get_rect()
      )
    except:
      print(self.color)
      exit()

    pygame.draw.ellipse(
      self.body, 
      self.genecolor,
      self.body.get_rect(),
      width=2
    )

    self.creatureSensorRadius = pygame.draw.circle(
      surface=surface, 
      color=pygame.Color(255,255,255), 
      center=self.rect.center,
      radius=self.body.get_width() * SENSOR_RANGE,
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
      self.rect.center,
      self.bodyRectImage.center,
      self.angle
    )

    # pygame.draw.rect(surface=surface, rect=self.rect, color=(0,255,255), width=1)
    # self.rect = pygame.draw.lines(
    #   surface=surface, 
    #   color=(0, 0, 0), 
    #   closed=True, 
    #   points=[self.rectp0, self.rectp1, self.rectp2, self.rectp3], 
    #   width=1
    # )

    
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
      radius=self.body.get_width() * ANTENNA_RANGE_SCALER,
      width=1,
    )

    self.rightAntennaRadius = pygame.draw.circle(
      surface=surface, 
      color=pygame.Color(255,255,255), 
      center=self.rightAntennaEnd,
      radius=self.body.get_width() * ANTENNA_RANGE_SCALER,
      width=1,
    )

    # self.velLine = pygame.draw.line(
    #   surface=surface,
    #   color=pygame.Color(0,255,0),
    #   start_pos=self.rect.center,
    #   end_pos=np.array(self.rect.center) + 10 * self.vel,
    #   width = 2
    # )

    barStart = pygame.math.Vector2(self.rect.bottomright) + pygame.math.Vector2(5, 0)
    barEnd = pygame.math.Vector2(self.rect.bottomright) \
      - pygame.math.Vector2(-5, MAX_CREATURE_SIZE)

    energyLength = (self.energyLeft/self.genes.energyCap) * (barStart - barEnd)


    self.energyBar = pygame.draw.line(
      surface=surface,
      color=(255,255,255),
      start_pos=barStart,
      end_pos=barEnd,
      width=5
    )

    self.energyBar = pygame.draw.line(
      surface=surface,
      color=(0,255,0),
      start_pos=barStart,
      end_pos=barStart  - energyLength,
      width=5
    )