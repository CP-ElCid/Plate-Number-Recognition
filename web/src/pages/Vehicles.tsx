import { useEffect, useState } from "react";
import { vehicleApi } from "../api/vehicleApi";
import { toPhilippineTime } from "../utils/dateUtils";



interface Vehicle {
  id: number;
  name: string;
  plate_number: string;
  purpose: string;
  profile_picture?: string;
  date_registered: string;
}

export default function Vehicles() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [form, setForm] = useState({ name: "", plate_number: "", purpose: "", profile_picture: "" });
  const [imagePreview, setImagePreview] = useState<string>("");
  const [editingPlate, setEditingPlate] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [vehicleToDelete, setVehicleToDelete] = useState<Vehicle | null>(null);

  const load = async () => {
    const res = await vehicleApi.getAll();
    setVehicles(res.data);
  };

  useEffect(() => { load(); }, []);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64String = reader.result as string;
        setImagePreview(base64String);
        setForm({ ...form, profile_picture: base64String });
      };
      reader.readAsDataURL(file);
    }
  };

  const addVehicle = async (e: any) => {
    e.preventDefault();

    // Normalize plate number: uppercase, remove spaces and special characters
    const normalizedPlate = form.plate_number.toUpperCase().replace(/[\s\-]/g, '');

    // Validate plate number (alphanumeric only, 5-8 characters)
    if (!/^[A-Z0-9]+$/.test(normalizedPlate)) {
      alert('Plate number should only contain letters and numbers');
      return;
    }

    if (normalizedPlate.length < 5 || normalizedPlate.length > 8) {
      alert('Plate number should be between 5 and 8 characters');
      return;
    }

    await vehicleApi.create({ ...form, plate_number: normalizedPlate });
    setForm({ name: "", plate_number: "", purpose: "", profile_picture: "" });
    setImagePreview("");
    load();
  };

  const handleEdit = (vehicle: Vehicle) => {
    setEditingPlate(vehicle.plate_number);
    setForm({
      name: vehicle.name,
      plate_number: vehicle.plate_number,
      purpose: vehicle.purpose || "",
      profile_picture: vehicle.profile_picture || ""
    });
    setImagePreview(vehicle.profile_picture || "");
    setIsModalOpen(true);
  };

  const handleUpdate = async (e: any) => {
    e.preventDefault();
    if (editingPlate) {
      // Normalize plate number: uppercase, remove spaces and special characters
      const normalizedPlate = form.plate_number.toUpperCase().replace(/[\s\-]/g, '');

      // Validate plate number (alphanumeric only, 5-8 characters)
      if (!/^[A-Z0-9]+$/.test(normalizedPlate)) {
        alert('Plate number should only contain letters and numbers');
        return;
      }

      if (normalizedPlate.length < 5 || normalizedPlate.length > 8) {
        alert('Plate number should be between 5 and 8 characters');
        return;
      }

      await vehicleApi.update(editingPlate, { ...form, plate_number: normalizedPlate });
      setIsModalOpen(false);
      setEditingPlate(null);
      setForm({ name: "", plate_number: "", purpose: "", profile_picture: "" });
      setImagePreview("");
      load();
    }
  };

  const handleDelete = (vehicle: Vehicle) => {
    setVehicleToDelete(vehicle);
    setDeleteModalOpen(true);
  };

  const confirmDelete = async () => {
    if (vehicleToDelete) {
      await vehicleApi.remove(vehicleToDelete.plate_number);
      setDeleteModalOpen(false);
      setVehicleToDelete(null);
      load();
    }
  };

  const cancelDelete = () => {
    setDeleteModalOpen(false);
    setVehicleToDelete(null);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingPlate(null);
    setForm({ name: "", plate_number: "", purpose: "", profile_picture: "" });
    setImagePreview("");
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg">
      <h2 className="text-3xl font-bold text-white mb-6">🚗 Registered Vehicles</h2>

      <form onSubmit={addVehicle} className="mb-6 bg-gray-700 p-4 rounded-lg">
        <div className="flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs font-medium text-gray-400 mb-1">Name</label>
            <input
              placeholder="Owner name"
              value={form.name}
              onChange={e => setForm({ ...form, name: e.target.value })}
              className="bg-gray-600 text-white border-0 p-2 rounded-lg w-full placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              required
            />
          </div>

          <div className="flex-1 min-w-[150px]">
            <label className="block text-xs font-medium text-gray-400 mb-1">Plate Number</label>
            <input
              placeholder="Plate number"
              value={form.plate_number}
              onChange={e => setForm({ ...form, plate_number: e.target.value })}
              className="bg-gray-600 text-white border-0 p-2 rounded-lg w-full placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              required
            />
          </div>

          <div className="flex-1 min-w-[150px]">
            <label className="block text-xs font-medium text-gray-400 mb-1">Purpose</label>
            <input
              placeholder="Purpose (optional)"
              value={form.purpose}
              onChange={e => setForm({ ...form, purpose: e.target.value })}
              className="bg-gray-600 text-white border-0 p-2 rounded-lg w-full placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
          </div>

          <div className="flex-1 min-w-[180px]">
            <label className="block text-xs font-medium text-gray-400 mb-1">Profile Picture</label>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="bg-gray-600 text-white border-0 p-2 rounded-lg w-full text-xs file:mr-2 file:py-1 file:px-3 file:rounded file:border-0 file:bg-blue-600 file:text-white hover:file:bg-blue-700 file:cursor-pointer file:text-xs"
            />
          </div>

          {imagePreview && (
            <div className="flex items-center">
              <img
                src={imagePreview}
                alt="Preview"
                className="w-10 h-10 object-cover rounded-full border-2 border-blue-500"
              />
            </div>
          )}

          <button
            type="submit"
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 font-medium transition-colors text-sm"
          >
            Add Vehicle
          </button>
        </div>
      </form>

      <div className="overflow-auto bg-gray-700 rounded-lg max-h-[600px]">
        <table className="w-full text-left">
          <thead className="bg-gray-750 border-b border-gray-600 sticky top-0">
            <tr>
              <th className="p-4 text-white font-semibold bg-gray-750">Photo</th>
              <th className="p-4 text-white font-semibold bg-gray-750">Name</th>
              <th className="p-4 text-white font-semibold bg-gray-750">Plate</th>
              <th className="p-4 text-white font-semibold bg-gray-750">Purpose</th>
              <th className="p-4 text-white font-semibold bg-gray-750">Date</th>
              <th className="p-4 text-white font-semibold bg-gray-750">Actions</th>
            </tr>
          </thead>
          <tbody>
            {vehicles.length === 0 ? (
              <tr>
                <td colSpan={6} className="p-8 text-center text-gray-400">
                  No vehicles registered yet...
                </td>
              </tr>
            ) : (
              vehicles.map(v => (
                <tr key={v.id} className="border-b border-gray-600 hover:bg-gray-600 transition-colors">
                  <td className="p-4">
                    <img
                      src={v.profile_picture || "https://via.placeholder.com/60"}
                      alt={v.name}
                      className="w-12 h-12 rounded-full object-cover border-2 border-gray-500"
                    />
                  </td>
                  <td className="p-4 text-white">{v.name}</td>
                  <td className="p-4 text-white">{v.plate_number}</td>
                  <td className="p-4 text-gray-300">{v.purpose}</td>
                  <td className="p-4 text-gray-300">{toPhilippineTime(v.date_registered)}</td>
                  <td className="p-4">
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleEdit(v)}
                        className="bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-1 rounded transition-colors"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(v)}
                        className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded transition-colors"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold text-white">Edit Vehicle</h3>
              <button
                onClick={closeModal}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleUpdate}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Name</label>
                  <input
                    placeholder="Enter owner name"
                    value={form.name}
                    onChange={e => setForm({ ...form, name: e.target.value })}
                    className="bg-gray-700 text-white border-0 p-3 rounded-lg w-full placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Plate Number</label>
                  <input
                    placeholder="Enter plate number"
                    value={form.plate_number}
                    onChange={e => setForm({ ...form, plate_number: e.target.value })}
                    className="bg-gray-600 text-gray-400 border-0 p-3 rounded-lg w-full cursor-not-allowed"
                    disabled
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Purpose</label>
                  <input
                    placeholder="Enter purpose (optional)"
                    value={form.purpose}
                    onChange={e => setForm({ ...form, purpose: e.target.value })}
                    className="bg-gray-700 text-white border-0 p-3 rounded-lg w-full placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Profile Picture</label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    className="bg-gray-700 text-white border-0 p-3 rounded-lg w-full file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-600 file:text-white hover:file:bg-blue-700 file:cursor-pointer"
                  />
                </div>
              </div>

              {imagePreview && (
                <div className="mb-4 flex justify-center">
                  <div className="text-center">
                    <p className="text-sm text-gray-400 mb-2">Preview:</p>
                    <img
                      src={imagePreview}
                      alt="Preview"
                      className="w-32 h-32 object-cover rounded-full border-4 border-gray-600"
                    />
                  </div>
                </div>
              )}

              <div className="flex gap-3">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium transition-colors"
                >
                  Update Vehicle
                </button>
                <button
                  type="button"
                  onClick={closeModal}
                  className="flex-1 bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 font-medium transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteModalOpen && vehicleToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold text-white">Confirm Delete</h3>
              <button
                onClick={cancelDelete}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ×
              </button>
            </div>

            <div className="mb-6">
              <div className="flex items-center gap-4 mb-4">
                <img
                  src={vehicleToDelete.profile_picture || "https://via.placeholder.com/60"}
                  alt={vehicleToDelete.name}
                  className="w-16 h-16 rounded-full object-cover border-2 border-gray-500"
                />
                <div>
                  <p className="text-white font-semibold text-lg">{vehicleToDelete.name}</p>
                  <p className="text-gray-400">{vehicleToDelete.plate_number}</p>
                </div>
              </div>
              <p className="text-gray-300">
                Are you sure you want to delete this vehicle? This action cannot be undone.
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={confirmDelete}
                className="flex-1 bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 font-medium transition-colors"
              >
                Delete
              </button>
              <button
                onClick={cancelDelete}
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
