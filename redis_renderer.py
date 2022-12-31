#!/usr/bin/python3

import pygame
# import pygame_gui
import numpy as np
import orjson
import redis
from redis.commands.search.field import TextField
import time

from world import World
from creature import Creature
from config import *
from serialization import customEncoder

# intialize redis connections
r = redis.Redis()
genomeDB = r.from_url('redis://localhost:6380/0')
timeseriesDB = r.from_url('redis://localhost:6381/0')

# flushing data for debugging purposes for now
r.flushall() 
genomeDB.flushall()
timeseriesDB.flushall()

fitnessTS = timeseriesDB.ts()
fitnessTS.create('fitness')

# create indices
r.execute_command('FT.CREATE worldIdx ON JSON PREFIX 1 t: SCHEMA $.tick AS tick NUMERIC $.maxFitness as maxFitness NUMERIC')
genomeDB.execute_command('FT.CREATE genomes ON JSON PREFIX 1 gene: SCHEMA $.hash AS hash TEXT $.fitness as fitness NUMERIC')

def writeToRedis(world, prevFitness):
  # TODO: reading __dict__ like this is not ok...
  worldState = orjson.dumps(world.__dict__, 
    option=orjson.OPT_SERIALIZE_NUMPY, 
    default=customEncoder
  ) 
  worldState = orjson.loads(worldState)

  r.json().set(f't:{world.tick}', '$', worldState)
  # if world.maxFitness != prevFitness:
  #   fitnessTS.add("fitness", world.tick, world.maxFitness)
  #   prevFitness = world.maxFitness

  for c in world.creatureList:

    if not genomeDB.json().get('gene:' + c.geneHash):
      data = {
        'hash': c.geneHash, 
        'fitness': c.getFitness(),
        'genome': orjson.loads(orjson.dumps(
          c.genes, 
          option=orjson.OPT_SERIALIZE_NUMPY, 
          default=customEncoder
        ))
      }
      genomeDB.json().set('gene:' + data['hash'], '$', data)

    elif genomeDB.json().get('gene:' + c.geneHash, 'fitness') < c.getFitness():
      genomeDB.json().set('gene:' + c.geneHash, 'fitness', c.getFitness())



def main():
  pygame.init()

  WINDOWSIZE = (640, 640)

  pygame.display.set_caption('aybio')
  window_surface = pygame.display.set_mode(WINDOWSIZE, pygame.RESIZABLE | pygame.DOUBLEBUF)

  background = pygame.Surface(WORLDSIZE)

  clock = pygame.time.Clock()
  is_running = True

  world = World(borderDims=WORLDSIZE)
  MAX_FPS=240

  font = pygame.font.Font('freesansbold.ttf', 16)
  updateWindow = True
  ticksPassed = 0
  pauseSimulation = False
  while is_running:
    time_delta = clock.tick(MAX_FPS)/1000.0
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        is_running = False

      elif event.type == pygame.VIDEORESIZE:
        WINDOWSIZE = (event.w,event.h)
        window_surface = pygame.display.set_mode(WINDOWSIZE,pygame.RESIZABLE | pygame.DOUBLEBUF)

      elif event.type == pygame.MOUSEBUTTONDOWN:
        button1 = pygame.mouse.get_pressed(num_buttons=3)[0]
        if button1:
          pos = list(pygame.mouse.get_pos())
          widthScale = WORLDSIZE[0]/window_surface.get_width()
          heightScale = WORLDSIZE[1]/window_surface.get_height()
          pos[0] = pos[0] * widthScale
          pos[1] = pos[1] * heightScale
          for c in world.creatureList:
            c: Creature
            if c.rect.collidepoint(*pos):
              print(c.geneColor)
              print(c.age)
              print(c.energyLeft)
              print(c.getFitness())

      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_q:
          updateWindow = not(updateWindow)

        if event.key == pygame.K_p:
          pauseSimulation = not(pauseSimulation)

    if not(pauseSimulation):
      offscreen_surface = pygame.Surface(WORLDSIZE)
      # manager.update(time_delta)

      offscreen_surface.blit(background, (0, 0))

      ### simulation logic here
      world.update(offscreen_surface)
      writeToRedis(world)

      if updateWindow:
        offscreen_surface = pygame.transform.scale(offscreen_surface, WINDOWSIZE)

        window_surface.blit(offscreen_surface, (0,0))

        numText = font.render(f'Produced: {world.creatureGen}', True, (125,255,125), (0,0,125))
        fitText = font.render(f'Max. Fit: {world.maxFitness}', True, (125,255,125), (0,0,125))
        numTextRect = numText.get_rect()
        numTextRect.topleft = (0,0)
        fitTextRect = fitText.get_rect()
        fitTextRect.topleft = numTextRect.bottomleft
        window_surface.blit(numText, numTextRect)
        window_surface.blit(fitText, fitTextRect)


        pygame.display.flip()

      if ticksPassed % 240 == 0:
        fps = str(int(clock.get_fps()))
        print(fps)
      
      ticksPassed += 1

main()