from flask import Flask, request, jsonify
from flask import render_template
import orjson
from multiprocessing import shared_memory

app = Flask(__name__)
memAddrs = orjson.loads(open('memAddrs.txt', 'r').read())
pauseMem = shared_memory.SharedMemory(memAddrs['pause'])
pause = pauseMem.buf
simRunning = False

@app.route('/togglePause', methods=['GET', 'POST'])
def togglePause():
  global pause
  if request.method == "POST":
    pause[0] = int(not(pause[0]))
    return f'paused: {pause[0]}' 
  return None

@app.route('/setPause/<int:_pause>', methods=['GET', 'POST'])
def setPause(_pause):
  global pause
  if request.method == "POST":
    pause[0] = int(bool(_pause))
    return f'paused: {pause[0]}' 
  return None

@app.route('/getPause')
def getPause():
  return f'paused: {pause[0]}'

@app.route('/')
def index():
  return "wassup boii\n"

if __name__ == "__main__":
  app.run()
