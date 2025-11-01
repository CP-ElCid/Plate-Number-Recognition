import axiosClient from "./axiosClient";

export const vehicleApi = {
  getAll: () => axiosClient.get("/vehicles"),
  getByPlate: (plate: string) => axiosClient.get(`/vehicles/${plate}`),
  create: (data: any) => axiosClient.post("/vehicles", data),
  update: (plate: string, data: any) => axiosClient.put(`/vehicles/${plate}`, data),
  remove: (plate: string) => axiosClient.delete(`/vehicles/${plate}`),
};
