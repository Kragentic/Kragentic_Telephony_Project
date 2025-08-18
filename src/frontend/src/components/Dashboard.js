import React, { useState, useEffect } from 'react';

const Dashboard = () => {
  const [calls, setCalls] = useState([]);
  const [consentRate, setConsentRate] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch call data and consent rate
    fetch('/api/calls')
      .then(response => response.json())
      .then(data => setCalls(data))
      .catch(error => setError(error.message));

    fetch('/api/consent-rate')
      .then(response => response.json())
      .then(data => setConsentRate(data.rate))
      .catch(error => setError(error.message));
  }, []);

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div>
      <h1>Agent/Manager Dashboard</h1>
      <div>
        <h2>Calls</h2>
        <ul>
          {calls.map(call => (
            <li key={call.id}>{call.phoneNumber} - {call.status}</li>
          ))}
        </ul>
      </div>
      <div>
        <h2>Consent Rate</h2>
        <p>{consentRate}%</p>
      </div>
    </div>
  );
};

export default Dashboard;
