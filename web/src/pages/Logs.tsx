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
    <div className="bg-gray-800 p-6 rounded-lg">
      <h2 className="text-3xl font-bold text-white mb-6">📋 Vehicle Logs</h2>

      <div className="overflow-auto bg-gray-700 rounded-lg">
        <table className="w-full text-left">
          <thead className="bg-gray-750 border-b border-gray-600">
            <tr>
              <th className="p-4 text-white font-semibold">Plate</th>
              <th className="p-4 text-white font-semibold">Status</th>
              <th className="p-4 text-white font-semibold">Time</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan={3} className="p-8 text-center text-gray-400">
                  No logs available yet...
                </td>
              </tr>
            ) : (
              logs.map(log => (
                <tr key={log.id} className="border-b border-gray-600 hover:bg-gray-600 transition-colors">
                  <td className="p-4 text-white">{log.plate_number}</td>
                  <td className={`p-4 font-semibold ${
                    log.status === "registered" ? "text-green-400" : "text-red-400"
                  }`}>
                    {log.status === "registered" ? "✅ Registered" : "🚫 Unregistered"}
                  </td>
                  <td className="p-4 text-gray-300">{new Date(log.timestamp).toLocaleString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
