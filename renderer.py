#!/usr/bin/python3

import pygame
import pygame_gui
import random
from world import World
from config import *

pygame.init()

WINDOWSIZE = (800, 800)

pygame.display.set_caption('aybio')
window_surface = pygame.display.set_mode(WINDOWSIZE, pygame.RESIZABLE)

background = pygame.Surface(WORLDSIZE)
background.fill(pygame.Color('#4cd645'))

manager = pygame_gui.UIManager(WINDOWSIZE)
# hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
#                                             text='Say Hello',
#                                             manager=manager)

clock = pygame.time.Clock()
is_running = True


world = World()

while is_running:
  time_delta = clock.tick(60)/1000.0
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      is_running = False

    elif event.type == pygame.VIDEORESIZE:
      WINDOWSIZE = (event.w,event.h)
      window_surface = pygame.display.set_mode(WINDOWSIZE,pygame.RESIZABLE)

    manager.process_events(event)


  offscreen_surface = pygame.Surface(WORLDSIZE)
  manager.update(time_delta)

  offscreen_surface.blit(background, (0, 0))

  ### simulation logic here
  coords = (
    random.randint(FOODSIZE[0], WORLDSIZE[0] - FOODSIZE[0]), 
    random.randint(FOODSIZE[1], WORLDSIZE[1] - FOODSIZE[1])
  )

  world.growFood(coords)
  world.drawAll(offscreen_surface)

  ### 

  offscreen_surface = pygame.transform.scale(offscreen_surface, WINDOWSIZE)

  window_surface.blit(offscreen_surface, (0,0))
  manager.draw_ui(window_surface)

  pygame.display.update()