// const redis = require("redis");
// const args = require('yargs').argv;
import * as redis from "redis";
import yargs from 'yargs/yargs';
import WebSocket from 'ws';

interface ConnectionState extends WebSocket.WebSocket{
  redisClient: redis.RedisClientType,
  worldStateSub: redis.RedisClientType,
  worldStateChannel: string,
  simServerAddr: string,
}

const args = yargs(process.argv).options({
  url: {type: 'string', default: '127.0.01'},
  redisPort: {type: 'number', default: 6379},
  wsPort: {type: 'number', default: 6969},
}).parseSync()

console.log('Firing up server with the following parameters:')
console.log('Redis URL: ' + args.url);
console.log('Redis port: ' + args.redisPort);
console.log('WebSocket port: ' + args.wsPort);

// const redis_client = redis.createClient(args.redisPort, 'redis');
const websocket_server = new WebSocket.Server({ port: args.wsPort });
const not_implemented = () => { console.log("welp, message handling function hasn't been implemented lol")};
console.log('Server Running!');


const MESSAGE_EVENT_HANDLERS: any = {
  // handle unsubscribing
  unsubscribe: async (socket: ConnectionState) => {
    await socket?.worldStateSub?.unsubscribe(socket.worldStateChannel);
    await socket?.worldStateSub?.disconnect();
  },

  // handle subscribing
  subscribe: async (socket: ConnectionState, channel: string) => {
    socket.worldStateSub = socket.redisClient.duplicate();
    await socket.worldStateSub.connect();
    socket.worldStateChannel = channel;
    await socket.worldStateSub.subscribe(socket.worldStateChannel, (message) => {
      socket.send(message);
    });
  },

  // run client-sent redis commands
  runCommand: async (socket: ConnectionState, command: Array<string>) => {
    let msg: Buffer = await socket.redisClient.sendCommand(command);
    socket.send(msg.toString("hex"));
  },

// TODO: something to be added later
//   sendCommandToSim: async (socket: ConnectionState, command: Array<string>) => {
//     let msg: Buffer = await socket.redisClient.sendCommand(command);

//     socket.send(msg.toString("hex"));
//   },
};

websocket_server.on('connection', (socket: ConnectionState, req) => {
  // Process incoming websocket messages:
  try { 
    // create new redis client
    socket.redisClient = redis.createClient({
      url: 'redis://' + args.url + ':' + args.redisPort
    });

    socket.redisClient.connect();
    // console.log({url: 'redis://' + args.url + ':' + args.redisPort})
  } catch(err) {
    socket.close();
  }

  socket.on('message', message => {
    let [action, payload] = message.toString().split(';');
    console.log(payload);
    console.log(payload.split(' '));
    try {
      let func = (MESSAGE_EVENT_HANDLERS[action] || not_implemented)(socket, payload.split(' '));
    }
    catch (err) {
      socket.close();
    }
  });

  socket.on('close', () => {
    MESSAGE_EVENT_HANDLERS.unsubscribe(socket);
    socket.redisClient.disconnect();
  });
});

// setInterval(() => {
// });