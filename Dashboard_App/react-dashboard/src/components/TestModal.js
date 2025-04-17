import React from 'react';
import './TestModal.css';

const TestModal = ({
  testScripts,
  selectedTestScript,
  handleTestScriptChange,
  uploadFile,
  handleFileChange,
  selectedModel,
  setSelectedModel,
  includePII,
  setIncludePII,
  showPiiEditor,
  setShowPiiEditor,
  userPrompt,
  setUserPrompt,
  guardrailsOptions,
  handleGuardrailChange,
  loading,
  onCancel,
  onStartTest
}) => {
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Commence Efficacy of Guardrails Test</h2>
        <p>
          This test will evaluate the performance and safety constraints of your selected model.
          Please choose your options below to begin.
        </p>

        <div className="form-group">
          <label htmlFor="test-script">Choose Test Script:</label>
          <select id="test-script" value={selectedTestScript} onChange={handleTestScriptChange}>
            {testScripts.map((script, index) => (
              <option key={index} value={script}>
                {script}
              </option>
            ))}
            <option value="upload-new">Upload New Test Script</option>
          </select>
        </div>

        {selectedTestScript === 'upload-new' && (
          <div className="form-group">
            <label htmlFor="upload-script">Select File:</label>
            <input
              id="upload-script"
              type="file"
              accept=".csv"
              onChange={handleFileChange}
            />
          </div>
        )}

        <div className="form-group">
          <label htmlFor="model-options">Choose Model:</label>
          <select
            id="model-options"
            value={selectedModel}
            onChange={e => setSelectedModel(e.target.value)}
          >
            {/* MODEL_OPTIONS are imported as a prop from the Dashboard or from a constants file */}
            {/** You can also pass MODEL_OPTIONS as a prop if needed. */}
            {require('../constants').MODEL_OPTIONS.map((model, index) => (
              <option key={index} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>

        {/* Section for PII Prevention */}
        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={includePII}
              onChange={(e) => setIncludePII(e.target.checked)}
            />
            Include PII Prevention in LLM Prompt
          </label>
          {includePII && (
            <div style={{ marginTop: "8px" }}>
              <button type="button" onClick={() => setShowPiiEditor(!showPiiEditor)}>
                Edit PII Prompt Warning (Optional)
              </button>
              {showPiiEditor && (
                <textarea
                  className="pii-textarea"
                  value={userPrompt}
                  onChange={(e) => setUserPrompt(e.target.value)}
                />
              )}
            </div>
          )}
        </div>
        
        <div className="form-group">
          <label>Select the Guardrails you would like to test:</label>
          <div>
            <label>
              <input type="checkbox" name="guardrailsAI-Profanity" />
              NeMo Guardrails - Toxicity Filtering
            </label>
          </div>
          <div>
            <label>
              <input type="checkbox" name="guardrailsAI-Profanity" />
              NeMo Guardrails - Topic Restrictions
            </label>
          </div>
          <div>
            <label>
              <input type="checkbox" name="guardrailsAI-Jailbreak" />
              GuardrailsAI - Jailbreak Response
            </label>
          </div>
          <div>
            <label>
              <input type="checkbox" name="guardrailsAI-Profanity" />
              Lakera Rebuff - Response Check
            </label>
          </div>
          <div>
            <label>
              <input type="checkbox" name="guardrailsAI-Profanity" />
              GuardrailsAI - Profanity Check
            </label>
          </div>
          <div>
            <label>
              <input
                type="checkbox"
                name="guardrailsAI"
                checked={guardrailsOptions.guardrailsAI}
                onChange={handleGuardrailChange}
              />
              GuardrailsAI - PII Detection
            </label>
          </div>
          <div>
            <label>
              <input
                type="checkbox"
                name="lakeraGuard"
                checked={guardrailsOptions.lakeraGuard}
                onChange={handleGuardrailChange}
              />
              Lakera Guard - Data Leakage
            </label>
          </div>
          <div>
            <label>
              <input
                type="checkbox"
                name="presidio"
                checked={guardrailsOptions.presidio}
                onChange={handleGuardrailChange}
              />
              Presidio - PII Detection
            </label>
          </div>
        </div>

        <div className="modal-buttons">
          <button onClick={onCancel} disabled={loading}>
            Cancel
          </button>
          <button onClick={onStartTest} disabled={loading}>
            {loading ? "Running..." : "Begin Test"}
          </button>
          {loading && <div className="loading-spinner" />}
        </div>
      </div>
    </div>
  );
};

export default TestModal;
