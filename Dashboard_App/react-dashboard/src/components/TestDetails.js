import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './TestDetails.css';

// A simple tab button component
const TabButton = ({ label, active, onClick }) => (
  <button
    className={`tab-button ${active ? 'active' : ''}`}
    onClick={onClick}
  >
    {label}
  </button>
);

// Component to display the test metadata
const TestMeta = ({ metadata }) => (
  <div className="test-meta">
    <p><strong>Model:</strong> {metadata.model || '—'}</p>
    <p><strong>Prompt Used:</strong> {metadata.prompt || '—'}</p>
    <p><strong>Expected Guardrails:</strong> {metadata.guardrails || '—'}</p>
  </div>
);

// Component that renders the table view of the test results
const TableView = ({ testResults }) => {
  return (
    <div className="results-table-wrapper">
      <div className="results-table-container">
        <table>
          <thead>
            <tr>
              {Object.keys(testResults[0]).map((key) => (
                <th key={key}>{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {testResults.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {Object.entries(row).map(([key, value], colIndex) => (
                  <td key={colIndex}>
                    <div className="truncate-wrapper">
                      <span className="truncated-text">
                        {String(value).length > 50
                          ? String(value).slice(0, 50) + "..."
                          : String(value)}
                      </span>
                      {String(value).length > 50 && (
                        <div className="tooltip-box">{String(value)}</div>
                      )}
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Component that renders the Data Visualisation view (placeholder)
const DataVisualisationView = () => (
  <div className="data-visualisation-container">
    <h3>Data Visualisation</h3>
  </div>
);

const TestDetail = () => {
  const { testID } = useParams();
  const navigate = useNavigate();
  const [testResults, setTestResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('dataviz'); // 'table' or 'dataviz'
  const [metadata, setMetadata] = useState({});


  useEffect(() => {
    fetch(`http://127.0.0.1:5000/api/tests/${testID}`)
      .then(res => {
        if (!res.ok) {
          throw new Error("Failed to fetch test results.");
        }
        return res.json();
      })
      .then(data => {
        setTestResults(data.results || []);
        setMetadata(data.metadata || {});
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching test details:", err);
        setError("Could not load test results.");
        setLoading(false);
      });
  }, [testID]);

  if (loading) return <div>Loading test results...</div>;
  if (error) return <div>{error}</div>;
  if (!Array.isArray(testResults) || testResults.length === 0) {
    return (
      <div className="test-detail-container">
        <button onClick={() => navigate(-1)} className="back-button">
          Back
        </button>
        <h2>No test results found for Test ID {testID}.</h2>
      </div>
    );
  }

  return (
    <div className="test-detail-container">
      <button onClick={() => navigate(-1)} className="back-button">
        Back
      </button>
      <h2>Test Results for ID: {testID}</h2>
      <TestMeta metadata={metadata} />
      
      {/* Tab Navigation Buttons */}
      <div className="tabs">
      <TabButton 
          label="Data Visualisation" 
          active={activeTab === 'dataviz'} 
          onClick={() => setActiveTab('dataviz')}
        />
        <TabButton 
          label="Data" 
          active={activeTab === 'table'} 
          onClick={() => setActiveTab('table')}
        />
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'table' ? (
          <TableView testResults={testResults} />
        ) : (
          <DataVisualisationView />
        )}
      </div>
    </div>
  );
};

export default TestDetail;
