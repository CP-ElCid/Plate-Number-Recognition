import { useEffect, useState } from "react";
import { logApi } from "../api/logApi";

interface Log {
  id: number;
  plate_number: string;
  status: string;
  timestamp: string;
}

export default function Logs() {
  const [logs, setLogs] = useState<Log[]>([]);

  const load = async () => {
    const res = await logApi.getAll();
    setLogs(res.data);
  };

  useEffect(() => { load(); }, []);

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Vehicle Logs</h2>
      <table>
        <thead>
          <tr><th>Plate</th><th>Status</th><th>Time</th></tr>
        </thead>
        <tbody>
          {logs.map(log => (
            <tr key={log.id}>
              <td>{log.plate_number}</td>
              <td>{log.status}</td>
              <td>{new Date(log.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
