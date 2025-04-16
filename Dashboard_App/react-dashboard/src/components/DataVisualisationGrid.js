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

/**
 * Helper function to extract guardrail names along with average and total values
 * from a pie chart data object.
 *
 * Expected format of keys (works for both with and without "Response"):
 *   "Average <Guardrail> Response Time (seconds)"  
 *   "Average <Guardrail> Time (seconds)"
 * And corresponding:
 *   "Total <Guardrail> Response Time (seconds)" or
 *   "Total <Guardrail> Time (seconds)"
 *
 * Returns an object { labels, avgValues, totalValues }.
 */
const extractGuardrailPieData = (chartDataObj) => {
  // The regex now captures an optional " Response" part.
  const guardrailRegex = /^Average (.+?)( Response)? Time \(seconds\)$/;
  const labels = [];
  const avgValues = [];
  const totalValues = [];
  
  Object.keys(chartDataObj).forEach((key) => {
    const match = key.match(guardrailRegex);
    if (match) {
      const guardrailName = match[1]; // e.g., "Raw" or "Lakera"
      const responsePart = match[2] || ""; // Either " Response" or empty string.
      // Only include if the value is not null/undefined.
      if (chartDataObj[key] !== undefined && chartDataObj[key] !== null) {
        labels.push(guardrailName);
        avgValues.push(chartDataObj[key]);
        // Construct the corresponding total key.
        const totalKey = `Total ${guardrailName}${responsePart} Time (seconds)`;
        totalValues.push(chartDataObj[totalKey] || 0);
      }
    }
  });
  
  return { labels, avgValues, totalValues };
};

/**
 * PieChart
 * Renders a pie chart that displays average values as the visible data.
 * On hover, the tooltip shows both the average and total times (each followed by "seconds")
 * on separate lines, along with an indication like "<Guardrail> Output".
 * The legend is displayed beneath the chart.
 * This version builds the labels and values dynamically – only guardrails that are in the data are shown.
 */
const PieChart = ({ data }) => {
  const chartDataObj = data[0] || {};
  const { labels, avgValues, totalValues } = extractGuardrailPieData(chartDataObj);
  
  const pieData = {
    labels,
    datasets: [
      {
        data: avgValues,
        // Use a preset palette—if there are more guardrails, colors will repeat.
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'],
      },
    ],
  };

  const options = {
    plugins: {
      title: {
        display: true,
        text: 'Time Distribution of Testing',
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
            const guardrail = context.chart.data.labels[index] || '';
            return [
              `${guardrail} Output`,
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
 * This version filters out any stage (row) where both Passed and Failed are zero,
 * so only guardrails/stages that were actually tested are displayed.
 */
const BarChartEffectiveness = ({ data }) => {
  // Filter out rows with no testing (i.e. Passed + Failed equals 0).
  const filteredData = data.filter(item => (item.Passed + item.Failed) > 0);
  
  const labels = filteredData.map((item) => item.Stage);
  const passedData = filteredData.map((item) => item.Passed);
  const failedData = filteredData.map((item) => item.Failed);

  // Compute the maximum total (Passed + Failed) for any stage.
  const maxTotal = Math.max(...filteredData.map(item => item.Passed + item.Failed));

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
        max: maxTotal,
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
 * 
 * This version:
 *   1. Dynamically detects which guardrails are in the data (so only those with data appear).
 *   2. Inverts 0 -> 1 (Pass) and 1 -> 0 (Fail), so Pass is drawn above Fail.
 *   3. Hides unused guardrails (those that are entirely null/undefined).
 *   4. Shows the prompt in the tooltip title, with each guardrail’s Pass/Fail on a separate line.
 *   5. Y-axis goes from -1 to 2, with 0 labeled “Fail,” 1 labeled “Pass,”
 *      and the outer ticks (-1, 2) hidden but leaving space for readability.
 */
const LineChartGuardrails = ({ data }) => {
  // Sort data by Test Number.
  const sortedData = [...data].sort(
    (a, b) => a['Test Number'] - b['Test Number']
  );

  // Extract the list of all potential guardrail keys from the first row (excluding known non-guardrail fields).
  const knownNonGuardrailFields = ['Test Number', 'User Prompt'];
  const allKeys = sortedData[0] ? Object.keys(sortedData[0]) : [];
  const guardrailKeys = allKeys.filter(
    (key) => !knownNonGuardrailFields.includes(key)
  );

  // Build datasets dynamically for each guardrail that's actually used (non-null/undefined in at least one row).
  // Invert 0 -> 1 (Pass) and 1 -> 0 (Fail).
  const colorPalette = [
    'rgba(255, 99, 132, 0.5)',
    'rgba(54, 162, 235, 0.5)',
    'rgba(255, 206, 86, 0.5)',
    'rgba(75, 192, 192, 0.5)',
    'rgba(153, 102, 255, 0.5)',
    'rgba(255, 159, 64, 0.5)',
  ];

  const isGuardrailUsed = (key) =>
    sortedData.some((row) => row[key] !== null && row[key] !== undefined);

  const datasets = guardrailKeys
    .filter(isGuardrailUsed)
    .map((key, index) => {
      const color = colorPalette[index % colorPalette.length];
      return {
        label: key,
        data: sortedData.map((row) => {
          if (row[key] === 0) return 1; // Pass becomes 1.
          if (row[key] === 1) return 0; // Fail becomes 0.
          return row[key];
        }),
        fill: false,
        borderColor: color,
        tension: 0.1,
        pointBackgroundColor: color,
      };
    });

  const testNumbers = sortedData.map((item) => item['Test Number']);

  const lineData = {
    labels: testNumbers,
    datasets,
  };

  const options = {
    maintainAspectRatio: false,
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
          title: function (context) {
            if (!context.length) return '';
            const idx = context[0].dataIndex;
            const testData = sortedData[idx];
            return testData?.['User Prompt'] || 'No Prompt Provided';
          },
          label: function (context) {
            const datasetLabel = context.dataset.label;
            const idx = context.dataIndex;
            const testData = sortedData[idx];
            const originalValue = testData[datasetLabel];
            const passFail =
              originalValue === 0 ? 'Pass' : originalValue === 1 ? 'Fail' : originalValue;
            return `${datasetLabel}: ${passFail}`;
          },
        },
      },
    },
    scales: {
      x: {
        ticks: {
          autoSkip: false,
        },
      },
      y: {
        min: -1,
        max: 2,
        ticks: {
          stepSize: 1,
          callback: function (value) {
            if (value === 0) return 'Fail';
            if (value === 1) return 'Pass';
            return '';
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
      {/* Bar Chart of Effectiveness */}
      <VizBlock id="successBarChart">
        <BarChartEffectiveness data={chartsData.successBarChart} />
      </VizBlock>
  
      {/* Pie Chart */}
      <VizBlock id="pieChart">
        <PieChart data={chartsData.pieChart} />
      </VizBlock>
  
      {/* Line Chart for Guardrail Pass/Fail per Test */}
      <VizBlock id="questionLineGraph">
        <LineChartGuardrails data={chartsData.questionLineGraph} />
      </VizBlock>
    </div>
  );  
};

export default DataVisualisationGrid;
