// /src/components/DashboardTable.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css'; // Consider if styling should be scoped or use CSS modules

const DashboardTable = ({ tests }) => {
  const navigate = useNavigate();

  return (
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
            <th>Prompt</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {tests.map((test, index) => (
            <tr
              key={index}
              onClick={() => navigate(`/test/${test.testID}`)}
              style={{ cursor: "pointer" }}
            >
              <td>{test.testID}</td>
              <td>{test.model}</td>
              <td>{test.testSet}</td>
              <td>{test.guardrails.join(', ')}</td>
              <td>{test.timeTaken}</td>
              <td>{test.date}</td>
              <td>{(test.piiPrompt || "").trim() !== "" ? "✔" : "✘"}</td>
              <td>
                {test.inProgress === true 
                  ? "In Progress"
                  : test.inProgress === false
                  ? "Completed"
                  : "Failed"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DashboardTable;
