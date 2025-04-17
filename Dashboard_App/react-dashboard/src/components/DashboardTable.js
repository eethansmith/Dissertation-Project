import React from 'react';
import { useNavigate } from 'react-router-dom';
import './DashboardTable.css';


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
            <th>Duration</th>
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
                {test.inProgress === true ? (
                <span className="status status-inprogress">in progress</span>
                ) : test.inProgress === false ? (
                <span className="status status-complete">completed</span>
                ) : (
                <span className="status status-failed">failed</span>
                )}
            </td>
            </tr>
        ))}
        </tbody>
      </table>
    </div>
  );
};

export default DashboardTable;
