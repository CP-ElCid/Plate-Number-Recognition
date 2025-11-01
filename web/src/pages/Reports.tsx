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
    <div style={{ padding: "1rem" }}>
      <h2>📈 Vehicle Reports</h2>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={data}>
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="registered" fill="#4CAF50" />
          <Bar dataKey="unregistered" fill="#F44336" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
