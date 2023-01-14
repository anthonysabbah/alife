
import WebSocket from 'ws';
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
import "chartjs-plugin-streaming";
import { useState, useEffect, useRef } from 'react';

type ConnectionInfo  = {
  url: string,
  port: number
};

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);



export default function RealtimeLineChart(connectionInfo: ConnectionInfo) {
  const [connection, setConnection] = useState(new WebSocket('ws://' + connectionInfo.url + ':' + connectionInfo.port));

  const config = useRef({
    responsive: true,
    type: "line",
    data: {
      datasets: [
        {
          label: "Max Fitness",
          data: []
        },
      ]
    }
  });

  const options = useRef({
    elements: {
      // line: {
      //   tension: 0.5
      // }
    },
    scales: {
      xAxes: [
        {
          type: "realtime",
          distribution: "linear",
          ticks: {
            displayFormats: 1,
            maxRotation: 0,
            minRotation: 0,
            stepSize: 1,
            maxTicksLimit: 240,
            // source: "auto",
            autoSkip: true,
          }
        }
      ],
      yAxes: [
        {
          ticks: {
            beginAtZero: true,
          }
        }
      ]
    }
  })

  useEffect(
    () => {
      connection.on('message', (rawMsg) => {
        const msg = rawMsg.toString('utf8');
        
      });
    }
  )
    
  return (
    <Line data={config.current.data}/>
  );
}