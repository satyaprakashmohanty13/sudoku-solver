import React from 'react';
export default function UploadForm({ onUpload }) {
  const handleChange = e => { if (e.target.files[0]) onUpload(e.target.files[0]); };
  return <input type="file" accept="image/*" onChange={handleChange} />;
}
