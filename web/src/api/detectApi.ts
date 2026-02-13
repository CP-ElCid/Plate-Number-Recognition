import axiosClient from "./axiosClient";

export const detectApi = {
  checkPlate: (plate: string) => axiosClient.post("/detect/manual", { plate_number: plate }),
};
