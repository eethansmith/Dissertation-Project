// App.js
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import TestDetail from './components/TestDetails';

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
