import React, { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { FaUpload } from 'react-icons/fa';
import axios from 'axios';

// Configuration for multiple backend endpoints
const ML_API_URL = 'http://localhost:5000';
const EXPRESS_API_URL = 'http://localhost:5000/api/signals';

const Home = () => {
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [analyzed, setAnalyzed] = useState(false);
  const [error, setError] = useState('');
  const [backendStatus, setBackendStatus] = useState('unknown');

  // Check backend status on component mount
  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        // Try multiple endpoints
        const endpoints = [
          'http://localhost:5000/api/health',
          'http://localhost:5000/health',
          'http://localhost:5000/'
        ];

        let response;
        for (const endpoint of endpoints) {
          try {
            response = await axios.get(endpoint, { timeout: 5000 });
            if (response.data) {
              console.log('Backend status:', response.data);
              setBackendStatus('online');
              return;
            }
          } catch (endpointError) {
            console.log(`Failed to connect to ${endpoint}:`, endpointError.message);
          }
        }

        // If no endpoint works
        setBackendStatus('offline');
      } catch (error) {
        console.error('Error checking backend status:', error);
        setBackendStatus('offline');
      }
    };

    checkBackendStatus();
  }, []);

  // Handle file drop 
  const onDrop = (acceptedFiles) => {
    setError('');
    const file = acceptedFiles[0];
    if (file) {
      console.log('File accepted:', file.name, file.type, file.size);
      setUploadedImage(file);

      // Create image preview
      const reader = new FileReader();
      reader.onload = (e) => {
        console.log('Image loaded successfully');
        setImagePreview(e.target.result);
      };
      reader.onerror = () => {
        console.log('Error reading file');
        setError('Error reading the image file');
      };
      reader.readAsDataURL(file);

      // Reset analyzed state when new image is uploaded
      setAnalyzed(false);
      setResult(null);
    }
  };

  // Handle file rejection
  const onDropRejected = (rejectedFiles) => {
    console.log('File rejected:', rejectedFiles);
    setError('Please upload a valid image file (jpg, png, gif) under 10MB');
  };

  // Dropzone configuration
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDropRejected,
    accept: {
      'image/jpeg': [],
      'image/png': [],
      'image/gif': [],
      'image/jpg': []
    },
    maxFiles: 1,
    maxSize: 10485760 // 10MB
  });

  // Process image through the API
  const processImage = async () => {
    if (!uploadedImage) {
      setError('Please upload an image first');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const formData = new FormData();
      formData.append('file', uploadedImage);

      console.log('Sending request to process image');
      console.log('Image file:', uploadedImage.name, uploadedImage.type, uploadedImage.size);

      // ML Prediction
      const predictionResponse = await axios.post(`${ML_API_URL}/predict`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 60000 // 60 seconds timeout
      });

      console.log('Prediction Response:', predictionResponse.data);

      // Create a well-formed result object based on the response
      const processedResult = {
        signalType: predictionResponse.data.class === 'Not a Valid Umpire Hand Signal'
          ? 'Invalid Signal'
          : predictionResponse.data.class,
        accuracy: predictionResponse.data.confidence ? predictionResponse.data.confidence * 100 : 0,
        meaning: predictionResponse.data.class === 'Not a Valid Umpire Hand Signal'
          ? 'No valid umpire hand signal detected'
          : getMeaningForSignal(predictionResponse.data.class),
        suggestions: predictionResponse.data.reason || 'Please upload a clear umpire hand signal image'
      };

      setResult(processedResult);
      setAnalyzed(true);
    } catch (error) {
      console.error('Error processing image:', error);

      if (error.code === 'ECONNABORTED') {
        setError('Request timed out. The server took too long to respond.');
      } else if (!error.response) {
        setError('Network error. Make sure the ML server is running at http://localhost:5000');
      } else {
        setError(error.response?.data?.error || 'Error processing image. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Helper function to get meaning for signal types
  const getMeaningForSignal = (signalType) => {
    const meanings = {
      'start_restart': 'Signal to start or restart the game',
      'direction_pass': 'Indicates direction of pass',
      'timeout': 'Signaling a timeout',
    };
    return meanings[signalType] || `${signalType} signal`;
  };


  // Generate suggestions based on accuracy
// Generate suggestions based on accuracy
const getSuggestions = () => {
  if (!result) return '';
  
  const handSignalsLink = "https://nsw.netball.com.au/sites/nsw/files/2022-10/HandSignals.pdf";
  let suggestion = '';
  
  // For invalid signals, return the reason or default message
  if (result.signalType === 'Invalid Signal') {
    suggestion = result.suggestions || 'Please upload a clear umpire hand signal image';
  } else {
    // Format confidence value to 2 decimal places
    const confidenceValue = (result.accuracy / 100).toFixed(2);
    
    // Generate confidence level text based on thresholds
    let confidenceLevel = '';
    let feedbackText = '';
    
    if (result.accuracy >= 90) {
      confidenceLevel = 'excellent';
      feedbackText = `Detection confidence is ${confidenceLevel} (${confidenceValue}). Signal is ${result.signalType}. Your signal execution is perfect! This would be an excellent example for training other umpires.`;
    } else if (result.accuracy >= 80) {
      confidenceLevel = 'very high';
      feedbackText = `Detection confidence is ${confidenceLevel} (${confidenceValue}). Signal is ${result.signalType}. Your signal is clear and well-executed, easily recognizable to players and coaches.`;
    } else if (result.accuracy >= 70) {
      confidenceLevel = 'high';
      feedbackText = `Detection confidence is ${confidenceLevel} (${confidenceValue}). Signal is ${result.signalType}. Your signal is good, but minor improvements in form could make it even clearer.`;
    } else if (result.accuracy >= 50) {
      confidenceLevel = 'moderate';
      feedbackText = `Detection confidence is ${confidenceLevel} (${confidenceValue}). Signal is ${result.signalType}. Your signal is recognizable but could use some practice to improve clarity.`;
    } else {
      confidenceLevel = 'low';
      feedbackText = `Detection confidence is ${confidenceLevel} (${confidenceValue}). Signal is ${result.signalType}. Your signal needs significant improvement to be clearly recognizable.`;
    }
    
    suggestion = feedbackText;
    
    // Add specific improvement suggestions for lower accuracy signals
    if (result.accuracy < 70) {
      if (result.signalType === 'start_restart') {
        suggestion += '\n\nTo improve this signal: Make sure your arms are fully extended and your motion is clear and decisive. Practice making the signal with more confidence and precision. Keep your body facing forward and ensure your arm movements are synchronized.';
      } else if (result.signalType === 'direction_pass') {
        suggestion += '\n\nTo improve this signal: Point more clearly with your arm fully extended. Make sure your body is positioned toward the direction you are indicating. Your arm should be straight and your fingers together, with a clear pointing gesture to indicate direction.';
      } else if (result.signalType === 'timeout') {
        suggestion += '\n\nTo improve this signal: Form a clear T shape with your hands. Keep your arms straight and make the gesture more pronounced. One palm should be vertical while the other horizontal, creating a distinct T shape at chest height.';
      }
    }
  }
  
  // Add the reference link at the end
  return `${suggestion}\n\nReference: ${handSignalsLink}`;
};

  // Save signal to backend
  const saveSignal = async () => {
    if (!uploadedImage || !result) {
      setError('Please analyze an image first');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const formData = new FormData();
      formData.append('file', uploadedImage);
      formData.append('signalType', result.signalType);
      formData.append('accuracy', result.accuracy);
      formData.append('meaning', result.meaning);
      formData.append('suggestions', getSuggestions());

      console.log('Saving signal data:', {
        signalType: result.signalType,
        accuracy: result.accuracy,
        meaning: result.meaning,
        file: uploadedImage.name
      });

      // Save to Express backend
      const saveResponse = await axios.post(EXPRESS_API_URL, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      console.log('Save response:', saveResponse.data);

      // Only show success for valid signals
      if (result.signalType !== 'Invalid Signal') {
        alert('Signal record saved successfully!');
      } else {
        alert('Cannot save an invalid signal.');
      }
    } catch (error) {
      console.error('Full error object:', error);
      console.error('Error response:', error.response);

      // More detailed error message
      const errorMessage = error.response?.data?.message ||
        error.response?.data?.error ||
        'Unexpected error occurred';

      setError(`Error saving signal: ${errorMessage}`);
      alert(`Error saving signal: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  // Handle clear button
  const handleClear = () => {
    setUploadedImage(null);
    setImagePreview('');
    setResult(null);
    setAnalyzed(false);
    setError('');
  };

  return (
    <div className="row">
      <div className="col-md-10 mx-auto">
        <div className="card">
          <div className="card-body">
            <h2 className="card-title text-center mb-4">Umpire Hand Signal Recognition</h2>

            {backendStatus === 'offline' && (
              <div className="alert alert-danger" role="alert">
                Backend server appears to be offline. Please start the servers.
              </div>
            )}

            {error && (
              <div className="alert alert-danger" role="alert">
                {error}
              </div>
            )}

            <div
              {...getRootProps({
                className: `dropzone ${isDragActive ? 'border-primary' : ''}`
              })}
            >
              <input {...getInputProps()} />
              <FaUpload className="upload-icon" style={{ fontSize: '3rem', marginBottom: '15px' }} />
              <p>Drag and drop an umpire hand signal image here, or click to select a file</p>
              {imagePreview && (
                <div className="mt-3" style={{ maxWidth: '200px', margin: '0 auto' }}>
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="img-fluid rounded"
                    style={{ maxHeight: '150px' }}
                  />
                </div>
              )}
            </div>

            {uploadedImage && !analyzed && (
              <div className="d-grid gap-2 mt-3">
                <button
                  className="btn btn-primary"
                  onClick={processImage}
                  disabled={loading || backendStatus !== 'online'}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Analyzing...
                    </>
                  ) : (
                    'Analyze Signal'
                  )}
                </button>
              </div>
            )}

            {loading && !analyzed && (
              <div className="text-center mt-4">
                <div className="spinner-border" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
                <p className="mt-2">Processing image...</p>
              </div>
            )}

            {analyzed && result && !loading && (
              <div className="mt-4">
                <div className="row">
                  <div className="col-md-6">
                    <div className="card">
                      <div className="card-body">
                        <h5 className="card-title">Uploaded Image</h5>
                        <div className="text-center">
                          <img
                            src={imagePreview}
                            alt="Umpire Signal"
                            className="img-fluid signal-image"
                            style={{ maxHeight: '300px' }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="col-md-6">
                    <div className="card">
                      <div className="card-body">
                        <h5 className="card-title">Signal Analysis</h5>

                        <div className="mb-3">
                          <label className="form-label">Signal Type</label>
                          <input
                            type="text"
                            className={`form-control ${result.signalType === 'Invalid Signal' ? 'text-danger' : ''}`}
                            value={result.signalType || ''}
                            readOnly
                          />
                        </div>

                        <div className="mb-3">
                          <label className="form-label">Accuracy</label>
                          <div className="accuracy-container">
                            <div className="progress">
                              <div
                                className="progress-bar"
                                role="progressbar"
                                style={{
                                  width: `${result.accuracy || 0}%`,
                                  backgroundColor: result.signalType === 'Invalid Signal'
                                    ? 'red'
                                    : result.accuracy > 70
                                      ? 'green'
                                      : result.accuracy > 40
                                        ? 'orange'
                                        : 'red'
                                }}
                                aria-valuenow={result.accuracy || 0}
                                aria-valuemin="0"
                                aria-valuemax="100"
                              >
                                {result.accuracy ? result.accuracy.toFixed(2) : 0}%
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="mb-3">
                          <label className="form-label">Meaning</label>
                          <input
                            type="text"
                            className={`form-control ${result.signalType === 'Invalid Signal' ? 'text-danger' : ''}`}
                            value={result.meaning || ''}
                            readOnly
                          />
                        </div>

                        <div className="mb-3">
  <label className="form-label">Suggestions</label>
  <div
    className={`form-control ${result.signalType === 'Invalid Signal' ? 'text-danger' : ''}`}
    style={{ height: 'auto', minHeight: '80px', padding: '0.375rem 0.75rem', overflow: 'auto' }}
    dangerouslySetInnerHTML={{
      __html: getSuggestions().split('\n').join('<br/>').replace(
        /(https?:\/\/[^\s]+)/g,
        '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
      )
    }}
  />
</div>

                        <div className="d-grid gap-2">
                          <button
                            type="button"
                            className="btn btn-success"
                            onClick={saveSignal}
                            disabled={loading || result.signalType === 'Invalid Signal' || backendStatus !== 'online'}
                          >
                            {loading ? 'Saving...' : 'Save'}
                          </button>
                          <button
                            type="button"
                            className="btn btn-danger"
                            onClick={handleClear}
                            disabled={loading}
                          >
                            Clear
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;