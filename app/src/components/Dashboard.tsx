import React, { useState } from 'react';
import {GlobalContext, defaultContext} from './GlobalContext';

import Button from '@mui/material/Button';
import LockIcon from '@mui/icons-material/Lock';
import LockOpenIcon from '@mui/icons-material/LockOpen';
// import Icon from '@mui/material/Icon';


import { WidthProvider, Responsive } from "react-grid-layout";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

import './Dashboard.css';
import ConnectionBox from './ConnectionBox';
import RealtimeLineChart from './RealtimeLineChart';
import GeneBox from './GeneBox';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export const options = {
  responsive: true,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    title: {
      display: true,
      text: 'Chart.js Line Chart',
    },
  },
};

const labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July'];

export const data = {
  labels,
  datasets: [
    {
      label: 'Dataset 1',
      data: [1, 2, 2, 5, 7, 2, 6],
      borderColor: 'rgb(255, 99, 132)',
      backgroundColor: 'rgba(255, 99, 132, 0.5)',
    },
    {
      label: 'Dataset 2',
      data: [1, 2, 4, 1, 2],
      borderColor: 'rgb(53, 162, 235)',
      backgroundColor: 'rgba(53, 162, 235, 0.5)',
    },
  ],
};



const ResponsiveReactGridLayout = WidthProvider(Responsive);
const originalLayouts = getFromLS("layouts") || [];

export default function Dashboard() {

  const [layouts, setLayout] = useState(JSON.parse(JSON.stringify(originalLayouts)));
  // const dashboardContext = useContext(GlobalContext);
  const [wsConn, setWsConn] = useState(defaultContext.wsConnection)
  const [isLocked, setIsLocked] = useState(false)

  const updateConn = (value: React.SetStateAction<string>) => {
    setWsConn(value)
  }

  const defState = {
    wsConnection: wsConn, 
    setWsConnection: updateConn
  }

  function saveLayout(layout: ReactGridLayout.Layout[], layouts: ReactGridLayout.Layouts) {
    saveToLS("layouts", layouts);
    setLayout(layouts);
  }

  function resetLayout() {
    setLayout({});
  }

  return (
    <GlobalContext.Provider value={defState}>
      <div>
        <div className="menu">

          <div className="menuItem">
            <Button variant="contained" onClick={resetLayout}>Reset Layout</Button>
          </div>


          {/* <div className="menuItem">
            <Button 
              variant="contained" 
              startIcon={isLocked ? <LockIcon/>: <LockOpenIcon/>}
              onClick={() => setIsLocked(!isLocked)}
            />
          </div> */}

          <div className="menuItem">
            <ConnectionBox/>
          </div>


          </div>
        <div>
          <ResponsiveReactGridLayout
            // {...this.props}
            layouts={layouts}
            onLayoutChange={ (layout, layouts) =>
              saveLayout(layout, layouts)
            }
          >
            <div key="1" className="layoutBox" data-grid={{ w: 2, h: 2, x: 0, y: 0, static: isLocked}}>
              <Button variant="contained" onClick={() => console.log(defaultContext)}>Log WS from Context</Button>
              <span className="text">1</span>
            </div>
            <div key="2" className="layoutBox" data-grid={{ w: 2, h: 2, x: 2, y: 0 }}>
              <span className="text">2</span>
              {/* <Line options={options} data={data} /> */}
            </div>
            <div key="3" className="layoutBox" data-grid={{ w: 2, h: 2, x: 4, y: 0 }}>
              <RealtimeLineChart/>
              {/* <span className="text"></span> */}
            </div>
            <div key="4" className="layoutBox" data-grid={{ w: 2, h: 2, x: 6, y: 0 }}>
              <GeneBox></GeneBox>
              <span className="text">4</span>
            </div>
            <div key="5" className="layoutBox" data-grid={{ w: 2, h: 2, x: 8, y: 0 }}>
              <span className="text">5</span>
            </div>
          </ResponsiveReactGridLayout>
        </div>
      </div>
    </GlobalContext.Provider>

  );
  }

  function saveToLS(key:string, value:any) {
    if (global.localStorage) {
      global.localStorage.setItem(
        "rgl-8",
        JSON.stringify({
          [key]: value
        })
      );
    }
  }

  function getFromLS(key:string) {
    let ls:any = {};
    if (global.localStorage) {
      try {
        ls = JSON.parse(global.localStorage.getItem("rgl-8") || '{}');
      } catch (e) {
        /*Ignore*/
      }
    }
    return ls[key];
  }