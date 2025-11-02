import { useEffect, useState } from "react";
import { logApi } from "../api/logApi";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";



export default function Reports() {
  const [data, setData] = useState<any[]>([]);

  const load = async () => {
    const res = await logApi.getAll();
    const logs = res.data;

    // Group by date
    const daily: Record<string, { registered: number; unregistered: number }> = {};

    logs.forEach((log: any) => {
      const date = new Date(log.timestamp).toLocaleDateString();
      if (!daily[date]) daily[date] = { registered: 0, unregistered: 0 };
      daily[date][log.status === "registered" ? "registered" : "unregistered"]++;
    });

    const chartData = Object.entries(daily).map(([date, counts]) => ({
      date,
      ...counts,
    }));

    setData(chartData);
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="bg-gray-800 p-6 rounded-lg">
      <h2 className="text-3xl font-bold text-white mb-6">📈 Vehicle Reports</h2>

      <div className="bg-gray-700 p-6 rounded-lg">
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data}>
            <XAxis dataKey="date" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#374151',
                border: 'none',
                borderRadius: '0.5rem',
                color: '#fff'
              }}
            />
            <Bar dataKey="registered" fill="#10B981" name="Registered" />
            <Bar dataKey="unregistered" fill="#EF4444" name="Unregistered" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
