import axiosClient from "./axiosClient";

export const logApi = {
  getAll: () => axiosClient.get("/logs"),
};
