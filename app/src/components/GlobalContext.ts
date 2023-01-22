import React from 'react';

export const defaultContext = {
  wsConnection: "ws://localhost:6969",
  setWsConnection: (conn: string) => {},
};

export const GlobalContext = React.createContext(defaultContext);
