#!/usr/bin/python3

import pygame
# import pygame_gui
import numpy as np
from world import World
from creature import Creature
from config import *
import os
import cv2
import time

os.environ["SDL_VIDEODRIVER"] = "dummy"
WINDOWSIZE = (500, 500)
window_surface = pygame.Surface(WINDOWSIZE)
if 1:
    #some platforms might need to init the display for some parts of pygame.
    pygame.display.init()
    # window_surface = pygame.display.set_mode(WINDOWSIZE)
    window_surface = pygame.display.set_mode((1,1))


pygame.init()


# pygame.display.set_caption('aybio')
# window_surface = pygame.display.set_mode(WINDOWSIZE, pygame.RESIZABLE)


background = pygame.Surface(WORLDSIZE)
# background.fill(pygame.Color('#4cd645'))

# manager = pygame_gui.UIManager(WINDOWSIZE)
# hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
#                                             text='Say Hello',
#                                             manager=manager)

clock = pygame.time.Clock()
is_running = True

world = World(borderDims=WORLDSIZE)
MAX_FPS=300
toggleWindow = True

font = pygame.font.Font('freesansbold.ttf', 16)
ticksPassed = 0

while is_running:
  time_delta = clock.tick(MAX_FPS)/1000.0
  event = pygame.event.poll()
  if event.type == pygame.QUIT:
      is_running = False
      pygame.quit()
      quit()

  offscreen_surface = pygame.Surface(WORLDSIZE)
  # manager.update(time_delta)

  offscreen_surface.blit(background, (0, 0))

  ### simulation logic here
  coords = (
    np.random.randint(FOODSIZE[0], WORLDSIZE[0] - FOODSIZE[0]), 
    np.random.randint(FOODSIZE[1], WORLDSIZE[1] - FOODSIZE[1])
  )

  world.update(offscreen_surface)

  ### 



  # if toggleWindow:
  offscreen_surface = pygame.transform.scale(offscreen_surface, WINDOWSIZE)
  # window_surface.blit(offscreen_surface, (0,0))
  numText = font.render(f'Produced: {world.creatureGen}', True, (125,255,125), (0,0,125)) 
  fitText = font.render(f'Max. Fit: {world.maxFitness}', True, (125,255,125), (0,0,125))
  numTextRect = numText.get_rect()
  numTextRect.topleft = (0,0)
  fitTextRect = fitText.get_rect()
  fitTextRect.topleft = numTextRect.bottomleft
  offscreen_surface.blit(numText, numTextRect)
  offscreen_surface.blit(fitText, fitTextRect)

  fps = str(int(clock.get_fps()))
  if ticksPassed % 5 * 120 == 0:
    print(fps)
    pygame.image.save(offscreen_surface, 'static/rendered.jpg')

  #   SCREEN = pygame.surfarray.array3d(window_surface)
  #   #  convert from (width, height, channel) to (height, width, channel)
  #   view = SCREEN.transpose([1, 0, 2])

  #   #  convert from rgb to bgr
  #   img_bgr = cv2.cvtColor(view, cv2.COLOR_RGB2BGR)
  #   cv2.imshow('img', img_bgr)
  # if cv2.waitKey(1) & 0xFF == ord('q'):
  #   toggleWindow = not(toggleWindow)
  
  ticksPassed += 1



  # manager.draw_ui(window_surface)

  # pygame.display.update()