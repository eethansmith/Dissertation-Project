import React, { useEffect, useState } from 'react';
import './Dashboard.css';

const Dashboard = () => {
  const [tests, setTests] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/tests')
      .then(response => response.json())
      .then(data => setTests(data));
  }, []);

  return (
    <div className="dashboard-container">
      <div className="header">
        <button className="new-test-button">Start New Test</button>
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
  );
};

export default Dashboard;
