import React, { useState } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Spinner, Button, Alert } from 'react-bootstrap';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState('');
  const [error, setError] = useState('');

  const onFileChange = event => {
    setFile(event.target.files[0]);
  };

  const onFileUpload = async () => {
    setLoading(true);
    setError('');
    setDownloadUrl('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://127.0.0.1:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setDownloadUrl(response.data.message);
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError('An error occurred while uploading the file.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-5">
      <h1>Docx file repair</h1>
      <input type="file" onChange={onFileChange} />
      <Button onClick={onFileUpload} disabled={!file || loading} className="mt-3">
        {loading ? <Spinner animation="border" /> : 'Upload'}
      </Button>

      {loading && <p>Processing...</p>}

      {error && <Alert variant="danger" className="mt-3">{error}</Alert>}

      {downloadUrl && (
        <div className="mt-3">
          <a href={downloadUrl} download className="btn btn-primary">
            Download Fixed File
          </a>
        </div>
      )}
    </div>
  );
}

export default App;
