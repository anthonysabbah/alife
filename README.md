# SimpleLife - A 2D Artificial Life Sim
See [Simulator Overview](#simulator-overview) for information specfically regarding
the simulator itself which includes an extensive overview of creatures (genomes, brains, etc.), food, world mechanics, etc.
## Goals
- Streamlined - Stay simple.
- Speed - The simulator itself should be fast, and the chosen data store solution (redis) should be able to keep up with it at a reasonable rate. 
  - Trying to hit ~20FPS with `MIN_CREATURES=20`, `WORLDSIZE=(1500,1500)` and `DB_UPDATE_INC=1` on a Macbook Air M1 w/ 8GB RAM
    - The simulator is primarily bottlenecked by world state serialization and writes to redis (takes ~50ms so 20FPS). May end up ditching redis for sqlite3 due to networking overhead introduced by redis.
## Configuration
Edit simulator constants in [config.json](./config.json)\*\
Wouldn't recommend touching [docker-compose.yaml](./docker-compose.yaml) or anything
docker related for now.

\***NOTE:** [config.json](./config.json) gets overwritten on every run of the simulator 
when it is connected to redis, so it is highly recommended to keep a copy of it config in [config.temp.json](./config.json).
## Run
```
pip install requirements.txt
```
### Standalone - no persistance
```
python3 renderer.py
```
### With Redis (**WIP**) - persistance now working
```
docker compose up -d
python3 redis_renderer.py
```
The config file for redis, is in `redis/redis-stack.conf`. Point-in-time snapshots of the redis database are stored in `redis/data/dump.rdb`
### Extras
- Run with env. var `ALIFE_HEADLESS=1` to trick sdl into using a dummy display driver - can be used to 
run on machines without a display.
### Simulator Keybinds (not in headless mode)
- `q` - toggles headless mode (no window draw updates)
- `p`  - pauses the simulator 

Here's a short clip of it running:

https://user-images.githubusercontent.com/49330057/206451231-130c9e0a-e654-4da1-aed7-58bc2bc2df69.mp4


### REST API:
Currently, a toy implementation of a REST API using Flask is used to pause the simulator. This is useful if it is run in 
headless mode since pygame cannot process input. Just run `python server.py`. Since this implementation currently uses [shared memory](https://docs.python.org/3/library/multiprocessing.shared_memory.html) to modify the `pauseSimulation` it requires python 3.8+ to run.
Using the API is pretty self explanatory: 
- `POST` request to the `/togglePause` endpoint to toggle pausing the sim.
- `POST` request to `/setPause/{int:pause}` with `{int:pause}` being an integer (ideally `0` or `1`) to pause/play the sim.
- `GET`  request to `/getPause` gets the pause status of the simulation.



## TODO:
<!-- - **CONFIG IS NOT REALLY SYNCED BETWEEN REDIS AND THE SUM - You'll have to read it from worldDB redis instance and copy paste it into `config.json` when it is different from the JSON document value under the `'config'` key in redis**. -->
- Add unit testing for Creatures, Food, and World
  - Make sure to test gene hash consistency between data on redis and simulator memory
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
