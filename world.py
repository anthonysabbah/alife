import numpy as np
import OpenGL.GL as gl
from OpenGL import GLU # OpenGL Utility Library, extends OpenGL functionality
from OpenGL.arrays import vbo

from food import Food

class World(object):
  def __init__(self):
    