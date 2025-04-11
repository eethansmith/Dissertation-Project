// App.js
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './Dashboard';
import TestDetail from './TestDetails';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/test/:testID" element={<TestDetail />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
