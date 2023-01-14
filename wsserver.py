import asyncio
import websockets

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

async def handler(websocket):
  while True:
      message = await websocket.recv()
      print(message)


async def main():
  async with websockets.serve(handler, "", 8001):
      await asyncio.Future()  # run forever


# if __name__ == "__main__":
#   app.run()
