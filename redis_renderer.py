#!/usr/bin/python3

import os

try:
  if os.environ["ALIFE_HEADLESS"] == "1":
    os.environ["SDL_VIDEODRIVER"] = "dummy"
except:
  pass

import pygame
# import pygame_gui
import orjson
import redis
import torch
import numpy as np
from redis.commands.search.query import Query
from redis.commands.search.aggregation import AggregateRequest, Asc, Desc
from collections import OrderedDict
import time

from world import World
from food import Food
from geneutils import Genome
from brain import Brain
from creature import Creature
from config import *
from serialization import customEncoder
from multiprocessing import shared_memory

class Simulator(object):
# intialize redis connections
  def __init__(self):
    self.world = World(borderDims=WORLDSIZE)
    self.r = redis.Redis()
    self.genomeDB = self.r.from_url('redis://localhost:6380/0')

    pygame.init()

    self.WINDOWSIZE = (640, 640)

    pygame.display.set_caption('aybio')
    self.window_surface = pygame.display.set_mode(self.WINDOWSIZE, pygame.RESIZABLE | pygame.DOUBLEBUF)

    self.background = pygame.Surface(WORLDSIZE)

    self.clock = pygame.time.Clock()

    rLen = len(self.r.keys())
    gLen = len(self.genomeDB.keys())
    load = False
    if rLen > 1:
      if gLen > 1:
        load = True
      else:
        print('ERROR: ONE OF THE DBs are EMPTY WHILST THE OTHER IS NOT')
    elif gLen > 1:
        print('ERROR: ONE OF THE DBs are EMPTY WHILST THE OTHER IS NOT')

    if load:
      self.loadWorld()

    try:
      # create indices
      self.r.execute_command('FT.CREATE worldIdx ON JSON PREFIX 1 t: SCHEMA $.tick AS tick NUMERIC $.maxFitness as maxFitness NUMERIC')
      self.genomeDB.execute_command('FT.CREATE genomes ON JSON PREFIX 1 gene: SCHEMA $.hash AS hash TEXT $.fitness as fitness NUMERIC')
    except:
      # this is run when indices already exist
      print('*** pretty sure indices already exist, skipping index creation... ***')

    # dumping shared mem addrs for the web server to access
    self.pauseMem = shared_memory.SharedMemory(create=True, size=1)
    self.pauseSimulation = self.pauseMem.buf
    memAddrs = {'pause': self.pauseMem.name}
    f = open('memaddrs.txt', 'w')
    f.write(orjson.dumps(memAddrs).decode('utf8'))
    f.close()
  
  #TODO: use multiprocessing on some loading operations for speedup
  def loadWorld(self):
    state = self.r.ft('worldIdx').search(Query('*').sort_by('tick', asc=False).paging(0,1))
    worldState = orjson.loads(state.docs[0].json)

    self.world.__dict__.update(worldState)
    self.world.borders = pygame.Rect(self.world.borders)

    # query genomeDB for best genome with fitness and hash
    docs = self.genomeDB.ft('genomes').aggregate(
      query=AggregateRequest('*')
        .sort_by(Desc('@fitness'), max=1)
        .group_by(['@fitness', '@hash'])
    )

    h = docs.rows[0][3]
    genomeId = f'gene:{h.decode("utf8")}'
    bestGenome = self.genomeDB.json().get(genomeId, 'genome')
    bestGenome['neuronalConnections'] = OrderedDict({x:torch.Tensor(bestGenome['neuronalConnections'][x])
        for x in bestGenome['neuronalConnections'].keys()}) 

    # temp genome
    b = Brain()
    self.world.bestGenome = Genome(1,1,1,b.state_dict())
    # load best genome
    self.world.bestGenome.__dict__.update(bestGenome)

    docs = self.r.ft('worldIdx').aggregate(query=AggregateRequest('*').sort_by(Desc('@tick'), max=1))
    self.world.tick = int(docs.rows[0][1])
    latestTickKey = f't:{self.world.tick}'
    # torchRNGState = self.r.json().get(latestTickKey, 'torchRNGState')
    # npRNGState = self.r.json().get(latestTickKey, 'npRNGState')

    self.world.torchRNGState = torch.ByteTensor(self.world.torchRNGState)
    torch.random.set_rng_state(self.world.torchRNGState)

    npRNGState = list(self.world.npRNGState)
    self.world.npRNGState[1] = np.array(self.world.npRNGState[1])
    self.world.npRNGState = tuple(self.world.npRNGState)
    #TODO: input has to be an np array?
    np.random.set_state(self.world.npRNGState)

    creatureList = self.r.json().get(latestTickKey, 'creatureList')
    self.world.creatureList = []

    for c in creatureList:
      genome = self.genomeDB.json().get(f'gene:{c["geneHash"]}', 'genome')
      genome['neuronalConnections'] = OrderedDict({x:torch.Tensor(genome['neuronalConnections'][x])
        for x in genome['neuronalConnections'].keys()})
      
      #temp genome
      tempGenome = Genome(1,1,1,b.state_dict())
      tempGenome.__dict__.update(genome)
      genome = tempGenome

      creature = Creature(c['id'], genome, pygame.Rect(c['rect']).center)
      creature.energyLeft = c['energyLeft']
      creature.energyConsumed = c['energyConsumed']
      creature.fitness = c['fitness']
      creature.babiesMade = c['babiesMade']
      creature.color = c['color']

      self.world.creatureList.append(creature)
    
    foodList = self.r.json().get(latestTickKey, 'foodList')
    self.world.foodList = []
    
    for f in foodList:
      food = Food(pygame.Rect(f['rect']).center, f['size'], f['energyLeft'])
      self.world.foodList.append(food)
      

  def writeToRedis(self):
    # TODO: reading __dict__ like this is not ok...
    worldState = orjson.dumps(self.world.__dict__, 
      option=orjson.OPT_SERIALIZE_NUMPY, 
      default=customEncoder
    ) 
    worldState = orjson.loads(worldState)

    self.r.json().set(f't:{self.world.tick}', '$', worldState)

    for c in self.world.creatureList:

      if not self.genomeDB.exists('gene:' + c.geneHash):
        data = {
          'hash': c.geneHash, 
          'fitness': c.getFitness(),
          'genome': orjson.loads(orjson.dumps(
            c.genes, 
            option=orjson.OPT_SERIALIZE_NUMPY, 
            default=customEncoder
          ))
        }
        self.genomeDB.json().set('gene:' + data['hash'], '$', data)

      # elif self.genomeDB.json().get('gene:' + c.geneHash, 'fitness') < c.getFitness():
      #   self.genomeDB.json().set('gene:' + c.geneHash, 'fitness', c.getFitness())
      # we just update lol
      else:
        self.genomeDB.json().set('gene:' + c.geneHash, 'fitness', c.getFitness())


  def main(self):

    # move this to config
    is_running = True

    font = pygame.font.Font('freesansbold.ttf', 16)
    updateWindow = True

    try:
      if os.environ['ALIFE_HEADLESS'] == "1":
        updateWindow = False
    except:
      pass

    while is_running:
      # time_delta = clock.tick(MAX_FPS)/1000.0
      start = time.time()
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          is_running = False

        elif event.type == pygame.VIDEORESIZE:
          self.WINDOWSIZE = (event.w,event.h)
          self.window_surface = pygame.display.set_mode(self.WINDOWSIZE,pygame.RESIZABLE | pygame.DOUBLEBUF)

        elif event.type == pygame.MOUSEBUTTONDOWN:
          button1 = pygame.mouse.get_pressed(num_buttons=3)[0]
          if button1:
            pos = list(pygame.mouse.get_pos())
            widthScale = WORLDSIZE[0]/self.window_surface.get_width()
            heightScale = WORLDSIZE[1]/self.window_surface.get_height()
            pos[0] = pos[0] * widthScale
            pos[1] = pos[1] * heightScale
            for c in self.world.creatureList:
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
            self.pauseSimulation[0] = int(not(self.pauseSimulation[0]))

      if not(self.pauseSimulation[0]):
        self.offscreen_surface = pygame.Surface(WORLDSIZE)
        # manager.update(time_delta)

        self.offscreen_surface.blit(self.background, (0, 0))

        ### simulation logic here
        self.world.update(self.offscreen_surface)
        if self.world.tick % DB_UPDATE_INC == 0:
          self.writeToRedis()

        if updateWindow:
          self.offscreen_surface = pygame.transform.scale(self.offscreen_surface, self.WINDOWSIZE)

          self.window_surface.blit(self.offscreen_surface, (0,0))

          numText = font.render(f'Produced: {self.world.creatureGen}', True, (125,255,125), (0,0,125))
          fitText = font.render(f'Max. Fit: {self.world.maxFitness}', True, (125,255,125), (0,0,125))
          numTextRect = numText.get_rect()
          numTextRect.topleft = (0,0)
          fitTextRect = fitText.get_rect()
          fitTextRect.topleft = numTextRect.bottomleft
          self.window_surface.blit(numText, numTextRect)
          self.window_surface.blit(fitText, fitTextRect)


          pygame.display.flip()

        if self.world.tick % 240 == 0:
          F = 1/(time.time() - start)
          fps = str(int(self.clock.get_fps()))
          print(fps, F)


if __name__ == "__main__":
  s = Simulator()
  s.main()