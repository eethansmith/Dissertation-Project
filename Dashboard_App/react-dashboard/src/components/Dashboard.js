import React, { useEffect, useState } from 'react';
import DashboardTable from './DashboardTable';
import TestModal from './TestModal';
import { MODEL_OPTIONS, DEFAULT_PROMPT } from '../constants';
import {
  fetchTests,
  fetchTestScripts,
  uploadTestScriptFile,
  startTestApi
} from '../services/api';
import './DashboardContainer.css';

const Dashboard = () => {
  
  // State variables
  const [tests, setTests] = useState([]);
  const [testScripts, setTestScripts] = useState([]);
  const [selectedTestScript, setSelectedTestScript] = useState('');
  const [uploadFile, setUploadFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  
  // Model and prompt state
  const [selectedModel, setSelectedModel] = useState(MODEL_OPTIONS[0]);
  const [includePII, setIncludePII] = useState(false);
  const [showPiiEditor, setShowPiiEditor] = useState(false);
  const [userPrompt, setUserPrompt] = useState(DEFAULT_PROMPT);
  
  // Guardrail options state
  const [guardrailsOptions, setGuardrailsOptions] = useState({
    guardrailsAI: false,
    lakeraGuard: false,
    presidio: false
  });
  
  // Handler for guardrail checkboxes
  const handleGuardrailChange = (e) => {
    const { name, checked } = e.target;
    setGuardrailsOptions(prevState => ({ ...prevState, [name]: checked }));
  };

  // Load tests and test scripts on mount
  useEffect(() => {
    fetchTests().then(data => setTests(data));
    fetchTestScripts().then(data => {
      setTestScripts(data);
      if (data.length > 0) setSelectedTestScript(data[0]);
    });
  }, []);

  // Event handlers for TestModal inputs
  const handleTestScriptChange = (e) => {
    const value = e.target.value;
    setSelectedTestScript(value);
    if (value === 'upload-new') {
      setUploadFile(null);
    }
  };
  
  const handleFileChange = (e) => {
    setUploadFile(e.target.files[0]);
  };

  // Function to run the test
  const handleStartTest = async () => {
    setLoading(true);
    
    // Upload file if needed
    if (selectedTestScript === 'upload-new' && uploadFile) {
      const { newScripts } = await uploadTestScriptFile(uploadFile);
      setTestScripts(newScripts);
      setSelectedTestScript(newScripts[newScripts.length - 1]);
    }
    
    const finalUserPrompt = includePII ? userPrompt : "";
    const payload = {
      model: selectedModel,
      testScript: selectedTestScript,
      userPrompt: finalUserPrompt,
      guardrails: guardrailsOptions
    };
    
    // Close modal and stop spinner immediately for a "fire and forget" start
    setShowModal(false);
    setLoading(false);
    
    startTestApi(payload)
      .then(response => {
        console.log('Test started:', response);
        const pollUntilComplete = () => {
          fetchTests()
            .then(data => {
              setTests(data);
              const test = data.find(t => t.testID === response.testID);
              if (test && test.inProgress === true) {
                setTimeout(pollUntilComplete, 3000);
              }
            })
            .catch(err => {
              console.error("Error polling for test status:", err);
              setTimeout(pollUntilComplete, 3000);
            });
        };
        pollUntilComplete();
      })
      .catch(error => {
        console.error('Error starting test:', error);
      });
  };

  return (
    <>
      <div className={`dashboard-container ${showModal ? 'blur-background' : ''}`}>
        <h1 className="dashboard-title">
          Efficacy of Guardrails for Large Language Models Dashboard
        </h1>
        <button className="new-test-button" onClick={() => setShowModal(true)}>
          Start New Test
        </button>
        <DashboardTable tests={tests} />
      </div>

      {showModal && (
        <TestModal
          testScripts={testScripts}
          selectedTestScript={selectedTestScript}
          handleTestScriptChange={handleTestScriptChange}
          uploadFile={uploadFile}
          handleFileChange={handleFileChange}
          selectedModel={selectedModel}
          setSelectedModel={setSelectedModel}
          includePII={includePII}
          setIncludePII={setIncludePII}
          showPiiEditor={showPiiEditor}
          setShowPiiEditor={setShowPiiEditor}
          userPrompt={userPrompt}
          setUserPrompt={setUserPrompt}
          guardrailsOptions={guardrailsOptions}
          handleGuardrailChange={handleGuardrailChange}
          loading={loading}
          onCancel={() => setShowModal(false)}
          onStartTest={handleStartTest}
        />
      )}
    </>
  );
};

export default Dashboard;
