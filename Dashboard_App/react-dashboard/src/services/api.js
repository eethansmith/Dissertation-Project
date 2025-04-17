// /src/services/api.js

const BASE_URL = 'http://127.0.0.1:5000/api';

export const fetchTests = () => {
  return fetch(`${BASE_URL}/tests`).then(res => res.json());
};

export const fetchTestScripts = () => {
  return fetch(`${BASE_URL}/test-scripts`).then(res => res.json());
};

export const uploadTestScriptFile = (uploadFile) => {
  const formData = new FormData();
  formData.append('file', uploadFile);

  return fetch(`${BASE_URL}/upload-test-script`, {
    method: 'POST',
    body: formData,
  })
    .then(res => res.json())
    .then(data => {
      // After a successful upload, refetch test scripts.
      return fetchTestScripts().then(newScripts => {
        return { uploadData: data, newScripts };
      });
    });
};

export const startTestApi = (payload) => {
  return fetch(`${BASE_URL}/start-test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }).then(res => res.json());
};
