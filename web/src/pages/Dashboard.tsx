import { useEffect, useState } from "react";
import { detectApi } from "../api/detectApi";

interface Detection {
  plate_number: string;
  status: string;
  timestamp: string;
}

export default function Dashboard() {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [plate, setPlate] = useState("");

  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/detections");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setDetections((prev) => [data, ...prev.slice(0, 10)]); // keep last 10 detections
    };

    ws.onclose = () => console.log("🔌 WebSocket disconnected");
    return () => ws.close();
  }, []);

  const checkManual = async () => {
    await detectApi.checkPlate(plate);
    setPlate("");
  };

  return (
    <div style={{ padding: "1rem" }}>
      <h2>🚗 Live Detection Dashboard</h2>
      <input
        value={plate}
        placeholder="Enter plate manually"
        onChange={(e) => setPlate(e.target.value)}
      />
      <button onClick={checkManual}>Check</button>

      <div style={{ marginTop: "2rem" }}>
        <h3>Live Updates</h3>
        <table>
          <thead>
            <tr><th>Plate</th><th>Status</th><th>Time</th></tr>
          </thead>
          <tbody>
            {detections.map((d, i) => (
              <tr key={i}>
                <td>{d.plate_number}</td>
                <td>{d.status === "registered" ? "✅" : "🚫"} {d.status}</td>
                <td>{new Date(d.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
