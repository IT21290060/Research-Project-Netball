import React, { useState, useEffect } from 'react';
import axios from 'axios';

const History = () => {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSignals();
  }, []);

  const fetchSignals = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/signals');
      setSignals(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching signals:', error);
      setLoading(false);
    }
  };

  const deleteSignal = async (id) => {
    if (window.confirm('Are you sure you want to delete this record?')) {
      try {
        await axios.delete(`http://localhost:5000/api/signals/${id}`);
        fetchSignals();
      } catch (error) {
        console.error('Error deleting signal:', error);
      }
    }
  };

  return (
    <div className="card">
      <div className="card-body">
        <h2 className="card-title text-center mb-4">Signal History</h2>
        
        {loading ? (
          <div className="text-center">
            <div className="spinner-border" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        ) : signals.length === 0 ? (
          <div className="alert alert-info">No signal records found.</div>
        ) : (
          <div className="table-responsive">
            <table className="table table-dark table-striped">
              <thead>
                <tr>
                  <th>Image</th>
                  <th>Signal Type</th>
                  <th>Accuracy</th>
                  <th>Meaning</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead> 
              <tbody>
                {signals.map((signal) => (
                  <tr key={signal._id}>
                    <td>
                      <img 
                        src={`http://localhost:5000${signal.imagePath}`} 
                        alt={signal.signalType} 
                        style={{ width: '50px', height: '50px', objectFit: 'cover' }}
                      />
                    </td>
                    <td>{signal.signalType}</td>
                    <td>{signal.accuracy.toFixed(2)}%</td>
                    <td>{signal.meaning}</td>
                    <td>{new Date(signal.createdAt).toLocaleString()}</td>
                    <td>
                      <button 
                        className="btn btn-sm btn-danger"
                        onClick={() => deleteSignal(signal._id)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default History;