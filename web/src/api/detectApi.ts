import axiosClient from "./axiosClient";

export const detectApi = {
  checkPlate: (plate: string) => axiosClient.post("/detect", { plate_number: plate }),
};
