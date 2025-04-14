// DataVisualisationGrid.jsx
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import VizBlock from './VizBlock';
import { Pie, Bar, Line } from 'react-chartjs-2';

// Import Chart.js components and react-chartjs-2 components.
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
} from 'chart.js';
  
// Register the components with ChartJS
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement
);

///////////////////////
// Reusable Components
///////////////////////

/**
 * PieChart
 * Renders a pie chart that displays average values as the visible data.
 * On hover, the tooltip shows both the average and total times (each followed by "seconds")
 * on separate lines, along with an indication like "Raw Output".
 * The legend is displayed beneath the chart.
 */
const PieChart = ({ data }) => {
  const chartDataObj = data[0] || {};

  const avgValues = [
    chartDataObj["Average Raw Response Time (seconds)"] || 0,
    chartDataObj["Average Lakera Time (seconds)"] || 0,
    chartDataObj["Average Presidio Time (seconds)"] || 0,
  ];
  const totalValues = [
    chartDataObj["Total Raw Response Time (seconds)"] || 0,
    chartDataObj["Total Lakera Time (seconds)"] || 0,
    chartDataObj["Total Presidio Time (seconds)"] || 0,
  ];

  const pieData = {
    labels: ['Raw', 'Lakera', 'Presidio'],
    datasets: [
      {
        data: avgValues,
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
      },
    ],
  };

  const options = {
    plugins: {
      title: {
        display: true,
        text: 'Time Distrubution of Testing',
        font: { size: 18 },
      },
      legend: {
        display: true,
        position: 'bottom',
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            const index = context.dataIndex;
            const testLabel = context.chart.data.labels[index] || '';
            return [
              `${testLabel} Output`,
              `Avg: ${avgValues[index]} seconds`,
              `Total: ${totalValues[index]} seconds`
            ];
          },
        },
      },
    },
  };

  return <Pie data={pieData} options={options} />;
};

/**
 * BarChartEffectiveness
 * Renders a grouped bar chart showing, per stage, the number of tests that Passed vs Failed.
 * The legend is positioned below the chart.
 */
const BarChartEffectiveness = ({ data }) => {
  const labels = data.map((item) => item.Stage);
  const passedData = data.map((item) => item.Passed);
  const failedData = data.map((item) => item.Failed);

  const barData = {
    labels,
    datasets: [
      {
        label: 'Passed',
        data: passedData,
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
      },
      {
        label: 'Failed',
        data: failedData,
        backgroundColor: 'rgba(255, 99, 132, 0.6)',
      },
    ],
  };

  const options = {
    plugins: {
      legend: {
        display: true,
        position: 'bottom',
      },
      title: {
        display: true,
        text: 'Effectiveness by Stage',
        font: { size: 18 },
      },
    },
  };

  return (
    <div>
      <Bar data={barData} options={options} />
    </div>
  );
};

/**
 * LineChartGuardrails
 * Renders a line chart where the x-axis is the test number,
 * and each line represents a guardrail (Raw, Lakera, Presidio).
 * The legend is positioned below the chart.
 */
const LineChartGuardrails = ({ data }) => {
  const sortedData = [...data].sort(
    (a, b) => a['Test Number'] - b['Test Number']
  );
  const testNumbers = sortedData.map((item) => item['Test Number']);
  const rawData = sortedData.map((item) => item.Raw);
  const lakeraData = sortedData.map((item) => item.Lakera);
  const presidioData = sortedData.map((item) => item.Presidio);

  const lineData = {
    labels: testNumbers,
    datasets: [
      {
        label: 'Raw',
        data: rawData,
        fill: false,
        borderColor: '#FF6384',
        tension: 0.1,
      },
      {
        label: 'Lakera',
        data: lakeraData,
        fill: false,
        borderColor: '#36A2EB',
        tension: 0.1,
      },
      {
        label: 'Presidio',
        data: presidioData,
        fill: false,
        borderColor: '#FFCE56',
        tension: 0.1,
      },
    ],
  };

  const options = {
    plugins: {
      legend: {
        display: true,
        position: 'bottom',
      },
      title: {
        display: true,
        text: 'Guardrail Pass/Fail per Test',
        font: { size: 18 },
      },
    },
  };

  return (
    <div>
      <Line data={lineData} options={options} />
    </div>
  );
};

///////////////////////
// Main Grid Component
///////////////////////

const DataVisualisationGrid = () => {
  const { testID } = useParams();

  const [chartsData, setChartsData] = useState({
    pieChart: [],
    successBarChart: [],
    questionLineGraph: [],
  });
  const [loadingCharts, setLoadingCharts] = useState(true);
  const [chartsError, setChartsError] = useState(null);

  useEffect(() => {
    fetch(`http://127.0.0.1:5000/api/tests/${testID}/charts`)
      .then((res) => {
        if (!res.ok) {
          throw new Error('Failed to fetch charts data.');
        }
        return res.json();
      })
      .then((data) => {
        setChartsData(data);
        setLoadingCharts(false);
      })
      .catch((err) => {
        console.error('Error fetching charts:', err);
        setChartsError('Failed to load charts data.');
        setLoadingCharts(false);
      });
  }, [testID]);

  if (loadingCharts)
    return <div style={{ textAlign: 'center' }}>Loading Chart Data...</div>;
  if (chartsError) return <div>{chartsError}</div>;

  return (
    <div className="data-viz-grid">
      {/* Pie Chart */}
      <VizBlock id="pieChart">
        <PieChart data={chartsData.pieChart} />
      </VizBlock>

      {/* Bar Chart of Effectiveness */}
      <VizBlock id="successBarChart">
        <BarChartEffectiveness data={chartsData.successBarChart} />
      </VizBlock>

      {/* Line Chart for Guardrail Pass/Fail per Test */}
      <VizBlock id="questionLineGraph">
        <LineChartGuardrails data={chartsData.questionLineGraph} />
      </VizBlock>
    </div>
  );
};

export default DataVisualisationGrid;
