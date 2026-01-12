import React, { useEffect, useState } from "react";
import "./App.css";

// 🔧 CONFIGURATION
// For Local: "ws://localhost:8000/ws"
// For Cloud: "wss://library-seat-backend.onrender.com/ws"
const WS_URL = "wss://library-seat-backend.onrender.com/ws"; 

function App() {
  const [data, setData] = useState({
    total: 0,
    occupied: 0,
    empty: 0,
    seats: {}, // Stores individual seat status
    last_updated: "Waiting...",
  });
  const [connectionStatus, setConnectionStatus] = useState("Disconnected");
  const [lastPacketTime, setLastPacketTime] = useState(Date.now());

  useEffect(() => {
    let ws;
    let reconnectInterval;

    const connect = () => {
      ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        setConnectionStatus("Connected");
        console.log("✅ WebSocket Connected");
      };

      ws.onmessage = (event) => {
        const liveData = JSON.parse(event.data);
        setData(liveData);
        setLastPacketTime(Date.now()); // Update heartbeat
      };

      ws.onclose = () => {
        setConnectionStatus("Reconnecting...");
        // Try to reconnect every 3 seconds
        reconnectInterval = setTimeout(connect, 3000);
      };
    };

    connect();

    // Cleanup on unmount
    return () => {
      if (ws) ws.close();
      if (reconnectInterval) clearTimeout(reconnectInterval);
    };
  }, []);

  // Check if data is "stale" (CV script hasn't sent data in > 5 seconds)
  const isStale = Date.now() - lastPacketTime > 5000 && connectionStatus === "Connected";

  return (
    <div className="dashboard-container">
      <header className="navbar">
        <div className="logo">📚 Dr BR Ambedkar Library Live Seat Occupancy</div>
        <div className={`status-pill ${connectionStatus === "Connected" ? "online" : "offline"}`}>
          {connectionStatus === "Connected" ? (isStale ? "⚠️ Live Feed Paused" : "● Live") : "○ Offline"}
        </div>
      </header>

      <main className="main-content">
        {/* TOP STATS ROW */}
        <div className="stats-grid">
          <div className="stat-card total">
            <h3>Total Capacity</h3>
            <h1>{data.total}</h1>
          </div>
          <div className="stat-card available">
            <h3>Available Now</h3>
            <h1>{data.empty}</h1>
          </div>
          <div className="stat-card occupied">
            <h3>Occupied</h3>
            <h1>{data.occupied}</h1>
          </div>
        </div>

        {/* VISUAL SEAT MAP */}
        <div className="seat-map-section">
          <h2>Live Floor Map</h2>
          <div className="legend">
            <span className="legend-item"><span className="dot green"></span> Available</span>
            <span className="legend-item"><span className="dot red"></span> Occupied</span>
          </div>
          
          <div className="seat-grid">
            {Object.keys(data.seats).length > 0 ? (
              // Sort seat IDs numerically to keep them in order
              Object.keys(data.seats).sort((a, b) => parseInt(a) - parseInt(b)).map((seatId) => (
                <div 
                  key={seatId} 
                  className={`seat-box ${data.seats[seatId] === "OCCUPIED" ? "seat-occupied" : "seat-empty"}`}
                >
                  {seatId}
                </div>
              ))
            ) : (
              <p className="loading-text">Waiting for seat layout...</p>
            )}
          </div>
        </div>
      </main>

      <footer className="footer">
        <p>Last Sync: {data.last_updated}</p>
      </footer>
    </div>
  );
}

export default App;