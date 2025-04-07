import React from 'react';
import './Dashboard.css';

const Dashboard = () => {
  // Sample data for demonstration purposes.
  const tests = [
    {
      model: 'Model A',
      testSet: ['Test1', 'Test2'],
      guardrails: ['Guard1', 'Guard2'],
      timeTaken: 120,
      date: '10-04-23-15-30'
    },
    {
      model: 'Model B',
      testSet: ['Test3', 'Test4'],
      guardrails: ['Guard3'],
      timeTaken: 95,
      date: '11-04-23-16-00'
    }
  ];

  return (
    <div className="dashboard-container">
      <div className="header">
        <button className="new-test-button">Start New Test</button>
      </div>
      <div className="table-container">
        <table>
          <thead>
            <tr>
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
                <td>{test.model}</td>
                <td>{test.testSet.join(', ')}</td>
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
