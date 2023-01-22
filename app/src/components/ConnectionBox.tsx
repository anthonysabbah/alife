import {GlobalContext, defaultContext} from './GlobalContext';
import TextField from '@mui/material/TextField';
import React, { useContext, useState } from 'react';
import Button from '@mui/material/Button';


export default function ConnectionBox() {

  const [wsString, setWSString] = useState(defaultContext.wsConnection)
  const context = useContext(GlobalContext)

  return (

    <GlobalContext.Consumer>
      {({wsConnection, setWsConnection}) => (

        <div>
          <TextField 
            id="outlined-basic"
            label="WebSocket Server URL" 
            variant="standard" 
            value={wsString}
            onChange={(e) => {
              setWSString(e.target.value)
            }}
          />

          <Button 
            variant="contained"
            onClick={(e) => {
              if (wsString !== context.wsConnection){
                setWsConnection(wsString)
              }
            }}
          >
            Connect
          </Button>
        </div>

      )}
    </GlobalContext.Consumer>
  );
}