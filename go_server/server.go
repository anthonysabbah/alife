// Copyright 2015 The Gorilla WebSocket Authors. All rights reserved.
// Use of this source code is governed by a BSD-style
// license that can be found in the LICENSE file.

package main

import (
	"context"
	"flag"
	"html/template"
	"log"
	"net/http"
	"strings"

	"github.com/go-redis/redis/v9"
	"github.com/gorilla/websocket"
)

type ClientInfo struct {
  conn   *websocket.Conn
  rdb    *redis.Client
  pubsub *redis.PubSub
  ctx    *context.Context
}

var addr = flag.String("addr", "localhost:6969", "http service address")
var redisAddr = flag.String("r", "localhost:6379", "redis address")
var simAddr = flag.String("s", "localhost:5000", "alife simulator web API address")

var upgrader = websocket.Upgrader{} // use default options

func handleMessage(client ClientInfo, rawMsg []byte) {
  message := string(rawMsg)
  commandNParams := strings.Split(message, ";")
  command := commandNParams[0]
  params := make([]interface{}, 1)
  if len(commandNParams) > 1 {
    rawParams := strings.Split(commandNParams[1], " ")
    params = make([]interface{}, len(rawParams))
    for i, v := range rawParams {
      params[i] = v
    }
  }

  switch command {
  case "subscribe":
    client.pubsub = client.rdb.Subscribe(*client.ctx, "latestWorldState")
    defer client.pubsub.Close()
    ch := client.pubsub.Channel()
    for msg := range ch {
      // log.Print(msg.Channel, msg.Payload)
      client.conn.WriteMessage(1, []byte(msg.Payload)) //messageType = 1 since we're just sending text data
    }

  case "cmd":
    ret := client.rdb.Do(*client.ctx, params...)
    val := ret.String()
    client.conn.WriteMessage(1, []byte(val))

  case "togglePause":
    httpAddr := "http://" + *simAddr + "/togglePause"
    http.Post(httpAddr, "", nil)

  default:
    errMsg := []byte("not a valid command")
    client.conn.WriteMessage(1, errMsg)
  }

}

func echo(w http.ResponseWriter, r *http.Request) {
  // ws connection, context, and redis client
  upgrader.CheckOrigin = func(r *http.Request) bool { return true }
  c, err := upgrader.Upgrade(w, r, nil)
  ctx := context.Background()
  rdb := redis.NewClient(&redis.Options{
    Addr:     *redisAddr,
    Password: "", // no password set
    DB:       0,  // use default DB
  })

  client := ClientInfo{c, rdb, nil, &ctx}

  if err != nil {
    log.Print("upgrade:", err)
    return
  }
  defer client.conn.Close()
  defer client.rdb.Close()
  for {
    _, message, err := client.conn.ReadMessage()
    if err != nil {
      log.Println("read:", err)
      break
    }
    log.Printf("recv: %s", message)
    handleMessage(client, message)

    // err = c.WriteMessage(mt, message)
  }
}

func home(w http.ResponseWriter, r *http.Request) {
  homeTemplate.Execute(w, "ws://"+r.Host+"/")
}

func main() {
  flag.Parse()
  log.SetFlags(0)
  http.HandleFunc("/", echo)
  http.HandleFunc("/ui", home)
  go log.Fatal(http.ListenAndServe(*addr, nil))
}

// webpage for sending websockets packets to the server instance
var homeTemplate = template.Must(template.New("").Parse(`
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script>  
window.addEventListener("load", function(evt) {

    var output = document.getElementById("output");
    var input = document.getElementById("input");
    var ws;

    var print = function(message) {
        var d = document.createElement("div");
        d.textContent = message;
        output.appendChild(d);
        output.scroll(0, output.scrollHeight);
    };

    document.getElementById("open").onclick = function(evt) {
        if (ws) {
            return false;
        }
        ws = new WebSocket("{{.}}");
        ws.onopen = function(evt) {
            print(ws.url)
            print("OPEN");
        }
        ws.onclose = function(evt) {
            print("CLOSE");
            ws = null;
        }
        ws.onmessage = function(evt) {
            print("RESPONSE: " + evt.data);
        }
        ws.onerror = function(evt) {
            print("ERROR: " + evt.data);
        }
        return false;
    };

    document.getElementById("send").onclick = function(evt) {
        if (!ws) {
            return false;
        }
        print("SEND: " + input.value);
        ws.send(input.value);
        return false;
    };

    document.getElementById("close").onclick = function(evt) {
        if (!ws) {
            return false;
        }
        ws.close();
        return false;
    };

});
</script>
</head>
<body>
<table>
<tr><td valign="top" width="50%">
<p>Click "Open" to create a connection to the server, 
"Send" to send a message to the server and "Close" to close the connection. 
You can change the message and send multiple times.
<p>
<form>
<button id="open">Open</button>
<button id="close">Close</button>
<p><input id="input" type="text" value="Hello world!">
<button id="send">Send</button>
</form>
</td><td valign="top" width="50%">
<div id="output" style="max-height: 70vh;overflow-y: scroll;"></div>
</td></tr></table>
</body>
</html>
`))
