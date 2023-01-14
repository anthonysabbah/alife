import {GlobalContext, defaultContext} from './GlobalContext';
import { useContext, useState } from 'react';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';


export default function ConnectionBox() {

  const dashboardContext = useContext(GlobalContext);

  return (

    <TextField 
      id="outlined-basic"
      label="WebSocket Server URL" 
      variant="standard" 
      value={defaultContext.wsConnection}
    />

    // <GlobalContext.Consumer>
    //   {({wsConnection, setWsConnection}) => (


    //   )}
    // </GlobalContext.Consumer>
  );
}