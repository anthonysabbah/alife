# SimpleLife - A 2D Artificial Life Sim
See [Simulator Overview](#simulator-overview) for information specfically regarding
the simulator itself which includes an extensive overview of creatures (genomes, brains, etc.), food, world mechanics, etc.
## Goals
- Streamlined - Stay simple.
- Speed - The simulator itself should be fast, and the chosen data store solution (redis) should be able to keep up with it at a reasonable rate. 
  - Trying to hit 30FPS with `MIN_CREATURES=20` and `WORLDSIZE=(1500,1500)`
   in headless mode. Currently it runs at ~17FPS.
## Configuration
Edit simulator constants in [config.py](./config.py)\
Wouldn't recommend touching [docker-compose.yaml](./docker-compose.yaml) or anything
docker related for now.

## Run
```
pip install requirements.txt
```
### Standalone
```
python3 renderer.py
```
### With Redis (**WIP**) - basically has no data persistance
```
docker compose up -d
python3 redis_renderer.py
```
### Simulator Keybinds
- `q` - toggles headless mode (no window draw updates)
- `p`  - pauses the simulator 

Here's a short clip:
https://user-images.githubusercontent.com/49330057/206451231-130c9e0a-e654-4da1-aed7-58bc2bc2df69.mp4


## TODO:
- Add unit testing for Creatures, Food, and World
- Optimize the living crap out of the simulator - probs unnecessary cos this is just a prototype, I plan on building a more mature verison of it in a compiled like language C++ or perhaps Rust.
- Figure out how data is going to be stored (see [Architecture](#arch))

## <a name="arch"></a> Architecture:
![architecture](./imgs/architecture.png)
- Docker containers (worldDB, genomeDB, etc.) - **WIP**
- UI - incomplete
  - Planning on using Vue.js with d3.js


## Simulator Overview
**TODO: add more stuff here**

Insect-like creatures that eat, reproduce, repeat