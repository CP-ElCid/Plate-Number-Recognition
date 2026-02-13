import { useEffect, useState } from "react";
import { logApi } from "../api/logApi";
import { toPhilippineTime } from "../utils/dateUtils";



interface Log {
  id: number;
  plate_number: string;
  status: string;
  timestamp: string;
}

export default function Logs() {
  const [logs, setLogs] = useState<Log[]>([]);
  const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false);

  const load = async () => {
    const res = await logApi.getAll();
    setLogs(res.data);
  };

  useEffect(() => { load(); }, []);

  const handleClearLogs = async () => {
    try {
      await logApi.clearAll();
      setIsConfirmModalOpen(false);
      load(); // Reload the empty list
    } catch (error) {
      console.error("Failed to clear logs:", error);
      alert("Failed to clear logs. Please try again.");
    }
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-white">📋 Vehicle Logs</h2>
        <button
          onClick={() => setIsConfirmModalOpen(true)}
          className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 font-medium transition-colors"
          disabled={logs.length === 0}
        >
          🗑️ Clear All Logs
        </button>
      </div>

      <div className="overflow-auto bg-gray-700 rounded-lg max-h-[600px]">
        <table className="w-full text-left">
          <thead className="bg-gray-750 border-b border-gray-600 sticky top-0">
            <tr>
              <th className="p-4 text-white font-semibold bg-gray-750">Plate</th>
              <th className="p-4 text-white font-semibold bg-gray-750">Status</th>
              <th className="p-4 text-white font-semibold bg-gray-750">Time</th>
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
                  <td className="p-4 text-gray-300">{toPhilippineTime(log.timestamp)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Confirmation Modal */}
      {isConfirmModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold text-white">Confirm Clear Logs</h3>
              <button
                onClick={() => setIsConfirmModalOpen(false)}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ×
              </button>
            </div>

            <div className="mb-6">
              <p className="text-gray-300 mb-4">
                Are you sure you want to delete all logs? This action cannot be undone.
              </p>
              <div className="bg-yellow-900 border border-yellow-600 rounded-lg p-3">
                <p className="text-yellow-200 text-sm">
                  ⚠️ <strong>Warning:</strong> This will permanently delete all {logs.length} log entries from the database.
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleClearLogs}
                className="flex-1 bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 font-medium transition-colors"
              >
                Yes, Clear All Logs
              </button>
              <button
                onClick={() => setIsConfirmModalOpen(false)}
                className="flex-1 bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 font-medium transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
