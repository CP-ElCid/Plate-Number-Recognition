import { useEffect, useState } from "react";
import { detectApi } from "../api/detectApi";
import { logApi } from "../api/logApi";
import { toPhilippineTime, toPhilippineTimeOnly } from "../utils/dateUtils";


interface Detection {
  plate_number: string;
  status: string;
  timestamp: string;
  vehicle?: {
    name: string;
    purpose?: string;
    profile_picture?: string;
  };
}

export default function Dashboard() {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [plate, setPlate] = useState("");
  const [selectedVehicle, setSelectedVehicle] = useState<Detection | null>(null);
  const [cameraOn, setCameraOn] = useState(false);
  const [isSearchModalOpen, setIsSearchModalOpen] = useState(false);
  const [searchResult, setSearchResult] = useState<Detection | null>(null);

  const handleCameraToggle = async () => {
    if (cameraOn) {
      // Stop the camera
      try {
        await fetch("http://127.0.0.1:8000/api/stop_camera", { method: "POST" });
        console.log("Camera stopped");
      } catch (error) {
        console.error("Error stopping camera:", error);
      }
    }
    setCameraOn(!cameraOn);
  };

  // WebSocket connection with reconnection logic
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: ReturnType<typeof setTimeout>;
    let isIntentionallyClosed = false;

    const connect = () => {
      try {
        ws = new WebSocket("ws://127.0.0.1:8000/ws/detections");

        ws.onopen = () => {
          console.log("✅ WebSocket connected successfully");
          console.log("WebSocket ready state:", ws?.readyState);
        };

        ws.onmessage = (event) => {
          console.log("📨 WebSocket message received:", event.data);
          try {
            const data = JSON.parse(event.data);
            console.log("📊 Parsed detection data:", data);

            // Only show REGISTERED plates in Live Updates
            if (data.status === "registered") {
              setDetections((prev) => {
                const updated = [data, ...prev.slice(0, 10)];
                console.log("📋 Updated detections:", updated);
                return updated;
              });
              setSelectedVehicle(data);
              console.log("✅ Registered detection added to list:", data.plate_number);
            } else {
              console.log("⏭️ Skipping unregistered plate from Live Updates:", data.plate_number);
            }
          } catch (error) {
            console.error("❌ Error parsing WebSocket message:", error);
            console.error("Raw message:", event.data);
          }
        };

        ws.onerror = (error) => {
          console.error("WebSocket error:", error);
        };

        ws.onclose = () => {
          console.log("🔌 WebSocket disconnected");
          // Attempt to reconnect after 3 seconds if not intentionally closed
          if (!isIntentionallyClosed) {
            reconnectTimeout = setTimeout(() => {
              console.log("🔄 Attempting to reconnect WebSocket...");
              connect();
            }, 3000);
          }
        };
      } catch (error) {
        console.error("Failed to create WebSocket:", error);
        // Retry connection after 3 seconds
        reconnectTimeout = setTimeout(connect, 3000);
      }
    };

    connect();

    return () => {
      isIntentionallyClosed = true;
      clearTimeout(reconnectTimeout);
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const checkManual = async () => {
    // Normalize plate number: uppercase, remove spaces and special characters
    const normalizedPlate = plate.toUpperCase().replace(/[\s\-]/g, '');

    // Validate plate number (alphanumeric only, 5-8 characters)
    if (!normalizedPlate) {
      alert('Please enter a plate number');
      return;
    }

    if (!/^[A-Z0-9]+$/.test(normalizedPlate)) {
      alert('Plate number should only contain letters and numbers');
      return;
    }

    if (normalizedPlate.length < 5 || normalizedPlate.length > 8) {
      alert('Plate number should be between 5 and 8 characters');
      return;
    }

    const res = await detectApi.checkPlate(normalizedPlate);
    setPlate("");
    const data = res.data;

    // Don't add manual checks to live detections
    // Only show result in modal
    setSearchResult(data);
    setIsSearchModalOpen(true);
  };

  const closeSearchModal = () => {
    setIsSearchModalOpen(false);
    setSearchResult(null);
  };

  const handleAddToLogs = async () => {
    if (!searchResult) return;

    try {
      // Create log entry with current timestamp
      // The backend will use the current Philippine time when creating the log
      await logApi.create({
        plate_number: searchResult.plate_number,
        status: searchResult.status,
        // vehicle_id is optional - backend will look it up based on plate_number if needed
      });

      // Close modal and show success
      setIsSearchModalOpen(false);
      setSearchResult(null);
      alert('✅ Successfully added to logs with current date and time!');
    } catch (error) {
      console.error("Failed to add to logs:", error);
      alert("❌ Failed to add to logs. Please try again.");
    }
  };



  return (
    <div className="flex flex-col">
      {/* SINGLE ROW - All Three Sections */}
      <div className="flex flex-col lg:flex-row gap-4">
        {/* Camera Feed - Left Column */}
        <div className="flex-1 bg-[#1e1e2d] text-white p-4 rounded-xl shadow-lg">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              📷 Camera Feed
            </h3>
            <button
              onClick={handleCameraToggle}
              className={`px-4 py-2 rounded-md text-white ${
                cameraOn ? "bg-red-600 hover:bg-red-700" : "bg-green-600 hover:bg-green-700"
              }`}
            >
              {cameraOn ? "⏹ Stop Camera" : "▶ Start Camera"}
            </button>
          </div>

          <div className="bg-gray-900 rounded-lg h-[600px] flex items-center justify-center">
            {cameraOn ? (
              <img
                src="http://127.0.0.1:8000/api/video_feed"
                alt="Camera Feed"
                className="w-full h-full object-cover rounded-md"
              />
            ) : (
              <p className="text-gray-400">Camera is off</p>
            )}
          </div>
        </div>

        {/* Live Detection Dashboard - Middle Column */}
        <div className="flex-1 bg-gray-800 p-6 rounded-lg flex flex-col">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
            🚗 Live Detection Dashboard
          </h2>

          <div className="flex gap-3 mb-6">
            <input
              className="bg-gray-700 text-white border-0 p-3 rounded-lg flex-1 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter plate manually"
              value={plate}
              onChange={(e) => setPlate(e.target.value)}
            />
            <button
              onClick={checkManual}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium transition-colors"
            >
              Check
            </button>
          </div>

          <h3 className="text-xl font-semibold text-white mb-4">Live Updates</h3>

          <div className="flex-1 overflow-auto bg-gray-700 rounded-lg max-h-[500px]">
            <table className="w-full text-left">
              <thead className="bg-gray-750 border-b border-gray-600 sticky top-0">
                <tr>
                  <th className="p-4 text-white font-semibold bg-gray-750">Plate</th>
                  <th className="p-4 text-white font-semibold bg-gray-750">Status</th>
                  <th className="p-4 text-white font-semibold bg-gray-750">Time</th>
                </tr>
              </thead>
              <tbody>
                {detections.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="p-8 text-center text-gray-400">
                      No detections yet...
                    </td>
                  </tr>
                ) : (
                  detections.map((d, i) => (
                    <tr
                      key={i}
                      className="hover:bg-gray-600 cursor-pointer border-b border-gray-600 transition-colors"
                      onClick={() => setSelectedVehicle(d)}
                    >
                      <td className="p-4 text-white">{d.plate_number}</td>
                      <td
                        className={`p-4 font-semibold ${
                          d.status === "registered" ? "text-green-400" : "text-red-400"
                        }`}
                      >
                        {d.status === "registered" ? "✅ Registered" : "🚫 Unregistered"}
                      </td>
                      <td className="p-4 text-gray-300">{toPhilippineTimeOnly(d.timestamp)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Vehicle Info Panel - Right Column */}
        <div className="w-full lg:w-96 bg-gray-800 p-6 rounded-lg">
          {selectedVehicle ? (
            <div className="flex flex-col items-center space-y-6">
              {/* Profile Picture */}
              <img
                src={
                  selectedVehicle.vehicle?.profile_picture ||
                  "https://via.placeholder.com/200"
                }
                alt="Vehicle Owner"
                className="w-40 h-40 rounded-full object-cover border-4 border-gray-600 shadow-lg"
              />

              {/* Vehicle Details */}
              <div className="w-full space-y-4 text-center">
                <div className="border-b border-gray-600 pb-3">
                  <p className="text-sm text-gray-400 mb-1">Name</p>
                  <p className="text-lg font-semibold text-white">
                    {selectedVehicle.vehicle?.name || "N/A"}
                  </p>
                </div>

                <div className="border-b border-gray-600 pb-3">
                  <p className="text-sm text-gray-400 mb-1">Plate Number</p>
                  <p className="text-lg font-semibold text-white">
                    {selectedVehicle.plate_number}
                  </p>
                </div>

                <div className="pb-3">
                  <p className="text-sm text-gray-400 mb-1">Date of Entry</p>
                  <p className="text-lg font-semibold text-white">
                    {toPhilippineTime(selectedVehicle.timestamp)}
                  </p>
                </div>

                {selectedVehicle.vehicle?.purpose && (
                  <div className="border-t border-gray-600 pt-3">
                    <p className="text-sm text-gray-400 mb-1">Purpose</p>
                    <p className="text-md text-gray-300">
                      {selectedVehicle.vehicle.purpose}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-400 text-center">
                No detection yet...<br />
                <span className="text-sm">Vehicle information will appear here</span>
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Search Result Modal */}
      {isSearchModalOpen && searchResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold text-white">
                {searchResult.status === "registered" ? "✅ Vehicle Registered" : "🚫 Vehicle Unregistered"}
              </h3>
              <button
                onClick={closeSearchModal}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ×
              </button>
            </div>

            <div className="flex flex-col items-center space-y-6 w-full">
              {/* Profile Picture */}
              {searchResult.status === "registered" ? (
                <>
                  <img
                    src={
                      searchResult.vehicle?.profile_picture ||
                      "https://via.placeholder.com/200"
                    }
                    alt="Vehicle Owner"
                    className="w-40 h-40 rounded-full object-cover border-4 border-green-600 shadow-lg mx-auto"
                  />

                  {/* Vehicle Details */}
                  <div className="w-full space-y-4">
                    <div className="border-b border-gray-600 pb-3">
                      <p className="text-sm text-gray-400 mb-1">Name</p>
                      <p className="text-lg font-semibold text-white">
                        {searchResult.vehicle?.name || "N/A"}
                      </p>
                    </div>

                    <div className="border-b border-gray-600 pb-3">
                      <p className="text-sm text-gray-400 mb-1">Plate Number</p>
                      <p className="text-lg font-semibold text-white">
                        {searchResult.plate_number}
                      </p>
                    </div>

                    <div className="border-b border-gray-600 pb-3">
                      <p className="text-sm text-gray-400 mb-1">Date of Entry</p>
                      <p className="text-lg font-semibold text-white">
                        {toPhilippineTime(searchResult.timestamp)}
                      </p>
                    </div>

                    {searchResult.vehicle?.purpose && (
                      <div className="pb-3">
                        <p className="text-sm text-gray-400 mb-1">Purpose</p>
                        <p className="text-md text-gray-300">
                          {searchResult.vehicle.purpose}
                        </p>
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <div className="text-center space-y-4 w-full">
                  <div className="w-40 h-40 rounded-full bg-gray-700 flex items-center justify-center border-4 border-red-600 mx-auto">
                    <span className="text-6xl">🚫</span>
                  </div>
                  <div className="w-full space-y-4">
                    <div className="border-b border-gray-600 pb-3">
                      <p className="text-sm text-gray-400 mb-1">Plate Number</p>
                      <p className="text-lg font-semibold text-white">
                        {searchResult.plate_number}
                      </p>
                    </div>
                    <div className="pb-3">
                      <p className="text-sm text-gray-400 mb-1">Status</p>
                      <p className="text-lg font-semibold text-red-400">
                        This vehicle is not registered in the system
                      </p>
                    </div>
                    <div className="border-t border-gray-600 pt-3">
                      <p className="text-sm text-gray-400 mb-1">Time Checked</p>
                      <p className="text-md text-gray-300">
                        {toPhilippineTime(searchResult.timestamp)}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={handleAddToLogs}
                className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-medium transition-colors"
              >
                📝 Add to Logs Now
              </button>
              <button
                onClick={closeSearchModal}
                className="flex-1 bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 font-medium transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
