import React, { useState } from 'react';
import UploadForm from './components/UploadForm';
import SudokuGrid from './components/SudokuGrid';
import axios from 'axios';

export default function App() {
  const [solution, setSolution] = useState(null);
  const handleFile = async (file) => {
    const form = new FormData();
    form.append('file', file);
    const { data } = await axios.post(
      'https://<YOUR_RENDER_BACKEND_URL>/api/solve', form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    setSolution(data.solution);
  };
  return (
    <div className="container">
      <h1>Sudoku Solver</h1>
      <UploadForm onUpload={handleFile} />
      {solution && <SudokuGrid grid={solution} />}
    </div>
  );
}
