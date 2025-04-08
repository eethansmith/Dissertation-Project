import React, { useEffect, useState } from 'react';
import './Dashboard.css';

const MODEL_OPTIONS = [
  "openai/gpt-3.5-turbo",
  "openai/gpt-4o-mini",
  "google/gemini-pro",
  "anthropic/claude-3-haiku",
  "deepseek/deepseek-chat:free",
  "meta-llama/llama-3-8b-instruct"
];

const Dashboard = () => {
  const [tests, setTests] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedModel, setSelectedModel] = useState(MODEL_OPTIONS[0]);
  const [testScripts, setTestScripts] = useState([]);
  const [selectedTestScript, setSelectedTestScript] = useState('');

  useEffect(() => {
    // Fetch test results
    fetch('http://127.0.0.1:5000/api/tests')
      .then(res => res.json())
      .then(data => setTests(data));

    // Fetch test script options for the dropdown (optional, dynamic)
    fetch('http://127.0.0.1:5000/api/test-scripts')
      .then(res => res.json())
      .then(data => {
        setTestScripts(data);
        if (data.length > 0) setSelectedTestScript(data[0]);
      });
  }, []);

  const handleStartTest = () => {
    const payload = {
      model: selectedModel,
      testScript: selectedTestScript
    };

    fetch('http://127.0.0.1:5000/api/start-test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(response => {
      console.log('Test started:', response);
      setShowModal(false);
      // Optionally re-fetch tests or append the new one
      return fetch('http://127.0.0.1:5000/api/tests')
        .then(res => res.json())
        .then(data => setTests(data));
    })
    .catch(error => console.error('Error starting test:', error));
  };

  return (
    <>
      <div className={`dashboard-container ${showModal ? 'blur-background' : ''}`}>
        <div className="header">
          <button className="new-test-button" onClick={() => setShowModal(true)}>
            Start New Test
          </button>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>testID</th>
                <th>Model</th>
                <th>Test Set</th>
                <th>Guardrails</th>
                <th>Time Taken</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {tests.map((test, index) => (
                <tr key={index}>
                  <td>{test.testID}</td>
                  <td>{test.model}</td>
                  <td>{test.testSet}</td>
                  <td>{test.guardrails.join(', ')}</td>
                  <td>{test.timeTaken}</td>
                  <td>{test.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Commence Efficacy of Guardrails Test</h2>
            <p>
              This test will evaluate the performance and safety constraints of your selected model. Please choose your options below to begin.
            </p>

            <div className="form-group">
              <label htmlFor="test-script">Choose Test Script:</label>
              <select
                id="test-script"
                value={selectedTestScript}
                onChange={e => setSelectedTestScript(e.target.value)}
              >
                {testScripts.map((script, index) => (
                  <option key={index} value={script}>{script}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="model-options">Choose Model:</label>
              <select
                id="model-options"
                value={selectedModel}
                onChange={e => setSelectedModel(e.target.value)}
              >
                {MODEL_OPTIONS.map((model, index) => (
                  <option key={index} value={model}>{model}</option>
                ))}
              </select>
            </div>

            <div className="modal-buttons">
              <button onClick={() => setShowModal(false)}>Cancel</button>
              <button onClick={handleStartTest}>Begin Test</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Dashboard;
