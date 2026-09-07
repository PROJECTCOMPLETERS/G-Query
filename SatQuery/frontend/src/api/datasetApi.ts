import { apiRequest } from "./client";

import type {
  Dataset,
  QueryResponse,
  UploadResponse,
} from "../types/dataset";

export const uploadSatelliteFile = async (
  file: File
): Promise<UploadResponse> => {
  const formData = new FormData();

  formData.append("file", file);

  return apiRequest<UploadResponse>("/api/upload", {
    method: "POST",
    body: formData,
  });
};

export const getDataset = async (
  datasetId: string
): Promise<Dataset> => {
  return apiRequest<Dataset>(
    `/api/datasets/${datasetId}`
  );
};

export const submitQuery = async (
  query: string,
  datasetId?: string
): Promise<QueryResponse> => {
  return apiRequest<QueryResponse>("/api/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query,
      dataset_id: datasetId || null,
    }),
  });
};