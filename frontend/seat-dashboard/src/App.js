import React, { useEffect, useState } from "react";
import "./App.css";

// 🔧 CONFIGURATION
const WS_URL = "wss://library-seat-backend.onrender.com/ws"; 

function App() {
  const [data, setData] = useState({
    total: 0,
    occupied: 0,
    empty: 0,
    seats: {},
    last_updated: "Waiting...",
  });
  const [connectionStatus, setConnectionStatus] = useState("Disconnected");
  const [lastPacketTime, setLastPacketTime] = useState(Date.now());
  
  // ✨ NEW: State for the popup notification
  const [showPopup, setShowPopup] = useState(true);

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
        setLastPacketTime(Date.now());
      };

      ws.onclose = () => {
        setConnectionStatus("Reconnecting...");
        reconnectInterval = setTimeout(connect, 3000);
      };
    };

    connect();

    return () => {
      if (ws) ws.close();
      if (reconnectInterval) clearTimeout(reconnectInterval);
    };
  }, []);

  const isStale = Date.now() - lastPacketTime > 5000 && connectionStatus === "Connected";

  return (
    <div className="dashboard-container">
      {/* ✨ 1. BACKGROUND IMAGE OVERLAY */}
      <div className="background-image"></div>

      {/* ✨ 2. POPUP NOTIFICATION */}
      {showPopup && (
        <div className="notification-popup">
          <div className="popup-header">
            <span>⚠️ Computation Notice</span>
            <button onClick={() => setShowPopup(false)}>✖</button>
          </div>
          <p>
            System update received. Note: To conserve hosting resources, 
            heavy CV computation runs only during live illustration events, 
            not continuously 24/7.
          </p>
        </div>
      )}

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

      {/* ✨ 3. IMPROVED FOOTER WITH LINKS */}
      <footer className="footer">
        <div className="footer-info">
          <p>Last Sync: <strong>{data.last_updated}</strong></p>
          <p className="credits">Built with ❤️ for Loop Winter Works</p>
        </div>
        <div className="social-links">
          {/* Replace # with your actual profile links */}
          <a href="https://github.com/Subraj-Kumar" target="_blank" rel="noreferrer">GitHub</a>
          <a href="https://www.linkedin.com/in/subraj-kumar/" target="_blank" rel="noreferrer">LinkedIn</a>
          <a href="https://www.linkedin.com/company/loop-se/posts/" target="_blank" rel="noreferrer">Loop SOE</a>
        </div>
      </footer>
    </div>
  );
}

export default App;