import { useEffect, useState } from "react";
import { vehicleApi } from "../api/vehicleApi";

interface Vehicle {
  id: number;
  name: string;
  plate_number: string;
  purpose: string;
  date_registered: string;
}

export default function Vehicles() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [form, setForm] = useState({ name: "", plate_number: "", purpose: "" });

  const load = async () => {
    const res = await vehicleApi.getAll();
    setVehicles(res.data);
  };

  useEffect(() => { load(); }, []);

  const addVehicle = async (e: any) => {
    e.preventDefault();
    await vehicleApi.create(form);
    setForm({ name: "", plate_number: "", purpose: "" });
    load();
  };

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Registered Vehicles</h2>
      <form onSubmit={addVehicle}>
        <input placeholder="Name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}/>
        <input placeholder="Plate" value={form.plate_number} onChange={e => setForm({ ...form, plate_number: e.target.value })}/>
        <input placeholder="Purpose" value={form.purpose} onChange={e => setForm({ ...form, purpose: e.target.value })}/>
        <button type="submit">Add Vehicle</button>
      </form>

      <table>
        <thead>
          <tr><th>Name</th><th>Plate</th><th>Purpose</th><th>Date</th></tr>
        </thead>
        <tbody>
          {vehicles.map(v => (
            <tr key={v.id}>
              <td>{v.name}</td>
              <td>{v.plate_number}</td>
              <td>{v.purpose}</td>
              <td>{new Date(v.date_registered).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
