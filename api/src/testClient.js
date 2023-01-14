const ws = require('ws');

server = new ws.WebSocket('ws://127.0.0.1:6969');

server.on('open', () => {
  server.send('subscribe;latestWorldState');
});

server.on('message', (msg) =>{
  console.log(msg.toString('utf8'));
});


