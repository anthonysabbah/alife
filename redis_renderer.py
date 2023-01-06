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
from config import CONFIG
from serialization import customEncoder
from multiprocessing import shared_memory

class Simulator(object):
# intialize redis connections
  def __init__(self):
    self.config = CONFIG
    self.world = World(borderDims=self.config['WORLDSIZE'])
    self.r = redis.Redis()
    if not self.r.exists('CONFIG'):
      self.r.json().set('CONFIG', '$', self.config)

    pygame.init()

    self.WINDOWSIZE = (640, 640)

    pygame.display.set_caption('aybio')
    self.window_surface = pygame.display.set_mode(self.WINDOWSIZE, pygame.RESIZABLE | pygame.DOUBLEBUF)

    self.background = pygame.Surface(self.config['WORLDSIZE'])

    self.clock = pygame.time.Clock()

    rLen = len(self.r.keys('t:*'))
    if rLen > 1:
      self.loadWorld()

    # dumping shared mem addrs for the web server to access
    self.pauseMem = shared_memory.SharedMemory(create=True, size=1)
    self.pauseSimulation = self.pauseMem.buf
    memAddrs = {'pause': self.pauseMem.name}
    f = open('memaddrs.txt', 'w')
    f.write(orjson.dumps(memAddrs).decode('utf8'))
    f.close()
  
  #TODO: use multiprocessing on some loading operations for speedup
  def loadWorld(self):
    print('loading world state from redis')

    self.config = self.r.json().get('CONFIG')
    confFile = open('config.json', 'w+')
    dumpConf = orjson.dumps(self.config, option=orjson.OPT_INDENT_2).decode('utf8')
    confFile.write(dumpConf)

    state = self.r.ft('worldIdx').search(Query('*').sort_by('tick', asc=False).paging(0,1))
    worldState = orjson.loads(state.docs[0].json)

    self.world.__dict__.update(worldState)
    self.world.borders = pygame.Rect(self.world.borders)
    self.background = pygame.Surface((self.world.borders.width, self.world.borders.height))

    # query r for best genome with fitness and hash
    docs = self.r.ft('genomes').aggregate(
      query=AggregateRequest('*')
        .sort_by(Desc('@fitness'), max=1)
        .group_by(['@fitness', '@hash'])
    )

    h = docs.rows[0][3]
    genomeId = f'gene:{h.decode("utf8")}'
    bestGenome = self.r.json().get(genomeId, 'genome')
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
      genome = self.r.json().get(f'gene:{c["geneHash"]}', 'genome')
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
      creature.geneHash = c['geneHash']
      creature.geneColor = c['geneColor']
      creature.angle = c['angle']
      creature.age = c['age']
      creature.vel = c['vel']
      creature.outs = c['outs']

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
    w = orjson.loads(worldState)


    if self.world.tick % self.config['DB_UPDATE_INC'] == 0:
      self.r.json().set(f't:{self.world.tick}', '$', w)
    self.r.publish('latestWorldState', worldState)


    for c in self.world.creatureList:

      if not self.r.exists('gene:' + c.geneHash):
        print('new genome?')
        data = {
          'hash': c.geneHash, 
          'fitness': c.getFitness(),
          'genome': orjson.loads(orjson.dumps(
            c.genes, 
            option=orjson.OPT_SERIALIZE_NUMPY, 
            default=customEncoder
          ))
        }
        self.r.json().set('gene:' + data['hash'], '$', data)

      elif self.r.json().get('gene:' + c.geneHash, 'fitness') < c.getFitness():
        self.r.json().set('gene:' + c.geneHash, 'fitness', c.getFitness())

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

        elif event.type == pygame.KEYDOWN:
          if event.key == pygame.K_q:
            updateWindow = not(updateWindow)

          if event.key == pygame.K_p:
            self.pauseSimulation[0] = int(not(self.pauseSimulation[0]))

      if not(self.pauseSimulation[0]):
        self.offscreen_surface = pygame.Surface((self.world.borders.width, self.world.borders.height))
        # manager.update(time_delta)

        self.offscreen_surface.blit(self.background, (0, 0))

        ### simulation logic here
        self.world.update(self.offscreen_surface)
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