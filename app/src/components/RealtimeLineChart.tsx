import { GlobalContext, defaultContext } from './GlobalContext';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartData
} from 'chart.js';
import { Line } from 'react-chartjs-2';
// import "chartjs-plugin-streaming";
import { useState, useEffect, useRef } from 'react';
import useWebSocket from 'react-use-websocket';
import { useContext } from 'react';
import { TextField } from '@mui/material';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    // title: {
    //   display: true,
    //   text: 'Chart.js Line Chart',
    // },
  },
};



export default function RealtimeLineChart() {
  const connectionInfo = useContext(GlobalContext)
  const { sendMessage, lastMessage} = useWebSocket( 
    connectionInfo.wsConnection,
    {
      shouldReconnect: (closeEvent) => true
    }
    );

  const [count, setCount] = useState(30)
  const [msg, setMsg] = useState("cmd;TS.REVRANGE maxFitness - + count " + count)
  const [pollInterval, setPollInterval] = useState(20000)
  // const [recvdData, setRecvdData] = useState([])
  const defDatasets = {
    labels: [0],
    datasets: [{
      label: 'Max. Fitness',
      data: [0],
      borderColor: 'rgb(255, 99, 132)',
      backgroundColor: 'rgba(255, 99, 132, 0.5)',
    }],
  };

  const [datasets, setDatasets] = useState(defDatasets)

  const pollRedis = () => {
    if (count > 0){
      setMsg("cmd;TS.REVRANGE maxFitness - + count " + count)
      sendMessage(msg)
      console.log("SENDING MSG")
    }
  }

  const convertData = (d: string) => {
    let converted = []
    const data: any = JSON.parse(d.split(":")[1].trim().replaceAll(" ", ","))
    for (var i in data){
      converted.push({x: data[i][0], y: data[i][1]})
    }
    return converted
  }

  useEffect(() => {
    if (lastMessage != null) {
      console.log('got msg')
      const converted = convertData(lastMessage.data).reverse()
      const labels = converted.map((p, _) =>{
        return p.x
      })
      const vals = converted.map((p, _) =>{
        return p.y
      })

      const datasets = {
        labels: labels,
        datasets: [{
          label: 'Max. Fitness',
          data: vals,
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
        }],
      };

      setDatasets(datasets)

      console.log(labels)
      console.log(vals)
    }
    let timerId = setTimeout(pollRedis, pollInterval)  
    return () => clearTimeout(timerId)
  }, [lastMessage, pollInterval, count])
    
  return (
    <div className="graphDiv">
      <Line 
        data={datasets}
        options={options}
      > </Line>
      <TextField 
        id="outlined-basic"
        label="Polling interval (ms)" 
        variant="standard" 
        value={pollInterval}
        onChange={(e) => {
          setPollInterval(parseInt(e.target.value))
        }}
      />
      <TextField 
        id="outlined-basic"
        label="Max # of datapoints" 
        variant="standard" 
        value={count}
        onChange={(e) => {
          setCount(parseInt(e.target.value))
        }}
      />
    </div>
  );
}