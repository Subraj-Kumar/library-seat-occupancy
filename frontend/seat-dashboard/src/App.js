import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);


  useEffect(() => {

    const fetchInitialData = async () => {
      try {
        const response = await fetch("https://library-seat-backend.onrender.com");
        const result = await response.json();
        if (result.last_updated) setData(result);
      } catch (err) {
        console.error("Initial fetch failed", err);
      }
    };
    fetchInitialData();

    const ws = new WebSocket("ws://127.0.0.1:8000/ws");

    ws.onopen = () => {
      console.log("✅ WebSocket connected");
      setConnected(true);
    };

    ws.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      setData(payload);
    };

    ws.onerror = () => {
      console.log("❌ WebSocket error");
      setConnected(false);
    };

    ws.onclose = () => {
      console.log("🔌 WebSocket closed");
      setConnected(false);
    };

    return () => ws.close();
    }, []);

  return (
    <div className="container">
    <h1>📚 JNU Library Seat Availability</h1>

    {!connected && (
      <p className="error">Connecting to backend...</p>
    )}

    {connected && !data && (
      <p>Waiting for live data...</p>
    )}

    {connected && data && (
      <div className="card">
        <p><strong>Total Seats:</strong> {data.total}</p>
        <p className="occupied">
          <strong>Occupied:</strong> {data.occupied}
        </p>
        <p className="free">
          <strong>Available:</strong> {data.empty}
        </p>
        <p className="time">
          Last Updated: {data.last_updated}
        </p>
      </div>
    )}
  </div>
  );
}

export default App;