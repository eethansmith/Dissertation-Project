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

  // Compute the maximum total (Passed + Failed) for any stage
  const maxTotal = Math.max(...data.map(item => item.Passed + item.Failed));

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
    maintainAspectRatio: false, // allow chart to fill the container
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
    scales: {
      y: {
        beginAtZero: true,
        max: maxTotal, // force the y-axis maximum to the sum of passed and failed
      },
    },
  };

  return (
    // This container will stretch to fill the VizBlock space.
    <div style={{ width: '100%', height: '100%' }}>
      <Bar data={barData} options={options} />
    </div>
  );
};

/**
 * LineChartGuardrails
 * Renders a line chart where the x-axis is the test number, 
 * and each line represents a guardrail (Raw, Lakera, Presidio).
 * 
 * Changes in this version:
 *  - Transforms the data so that a guardrail originally 0 (Pass) now plots as 1,
 *    and a guardrail originally 1 (Fail) now plots as 0.
 *  - The y-axis spans from -1 to 2, but only the 0 and 1 ticks are labeled ("Fail" and "Pass")
 *    with Pass (1) displayed above Fail (0).
 *  - When hovering, the tooltip displays the User Prompt on the title line and then the guardrail result,
 *    using the original (untransformed) data.
 *  - The chart fills the available space.
 */
const LineChartGuardrails = ({ data }) => {
  // Sort data by Test Number.
  const sortedData = [...data].sort(
    (a, b) => a['Test Number'] - b['Test Number']
  );
  const testNumbers = sortedData.map((item) => item['Test Number']);
  
  // Transform original guardrail values so that:
  //   Original 0 (Pass) becomes 1, and original 1 (Fail) becomes 0.
  const rawDataTransformed = sortedData.map(item => 1 - item.Raw);
  const lakeraDataTransformed = sortedData.map(item => 1 - item.Lakera);
  const presidioDataTransformed = sortedData.map(item => 1 - item.Presidio);

  const lineData = {
    labels: testNumbers,
    datasets: [
      {
        label: 'Raw',
        data: rawDataTransformed,
        fill: false,
        borderColor: 'rgba(255, 99, 132, 0.5)',
        tension: 0.1,
        pointBackgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
      {
        label: 'Lakera',
        data: lakeraDataTransformed,
        fill: false,
        borderColor: 'rgba(54, 162, 235, 0.5)',
        tension: 0.1,
        pointBackgroundColor: 'rgba(54, 162, 235, 0.5)',
      },
      {
        label: 'Presidio',
        data: presidioDataTransformed,
        fill: false,
        borderColor: 'rgba(255, 206, 86, 0.5)',
        tension: 0.1,
        pointBackgroundColor: 'rgba(255, 206, 86, 0.5)',
      },
    ],
  };

  const options = {
    maintainAspectRatio: false, // Allow the chart to fill its container.
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
      tooltip: {
        callbacks: {
          // Use the User Prompt as the sole title of the tooltip.
          title: function (context) {
            if (!context.length) return '';
            const idx = context[0].dataIndex;
            const testData = sortedData[idx];
            return testData?.['User Prompt'] || 'No Prompt Provided';
          },
          // Show the guardrail type and the original (untransformed) result.
          label: function (context) {
            const idx = context.dataIndex;
            const testData = sortedData[idx];
            const originalVal = testData ? testData[context.dataset.label] : null;
            const resultText =
              originalVal === 0 ? 'Pass' : originalVal === 1 ? 'Fail' : originalVal;
            return `${context.dataset.label} Guardrail: ${resultText}`;
          },
        },
      },
    },
    scales: {
      x: {
        ticks: {
          autoSkip: false, // Display every test number.
        },
      },
      y: {
        min: -1,
        max: 2,
        ticks: {
          stepSize: 1,
          // Label only the 0 and 1 ticks. Here, 0 represents Fail and 1 represents Pass.
          callback: function (value) {
            if (value === 0) return 'Fail';
            if (value === 1) return 'Pass';
            return ''; // Hide the -1 and 2 labels.
          },
        },
      },
    },
  };

  return (
    <div style={{ width: '100%', height: '100%' }}>
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
