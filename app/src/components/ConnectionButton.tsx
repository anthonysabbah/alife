import {GlobalContext, defaultContext} from './GlobalContext';
import { useContext, useState } from 'react';
import Button from '@mui/material/Button';


export default function ConnectionBox() {

  const dashboardContext = useContext(GlobalContext);

  // return (
  //   <GlobalContext.Consumer>
  //     {({wsConnection, setWsConnection}) => (

  //     )}
  //   </GlobalContext.Consumer>
  // );
  return(
    <Button variant="contained">Connect</Button>
  );
}