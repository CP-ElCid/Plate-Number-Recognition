import axiosClient from "./axiosClient";

export const logApi = {
  getAll: () => axiosClient.get("/logs"),
  clearAll: () => axiosClient.delete("/logs/clear"),
  create: (data: { plate_number: string; status: string; vehicle_id?: number }) =>
    axiosClient.post("/logs", data),
};
