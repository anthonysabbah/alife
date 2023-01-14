import WebSocket from 'ws';
import React, { useContext, useState } from 'react';

export const defaultContext = {
  wsConnection: "ws://127.0.0.1:6969",
  setWsConnection: () => {},
};

export const GlobalContext = React.createContext(defaultContext);
