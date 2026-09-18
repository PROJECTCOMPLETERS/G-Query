import apiClient from "./client";

import type {
  CreateDatasetResponse,
  Dataset,
  DatasetListResponse,
  DatasetType,
  UploadDatasetFileResponse,
} from "../types/dataset";

export const createDataset = async (
  name: string,
  datasetType: DatasetType,
  signal?: AbortSignal
): Promise<CreateDatasetResponse> => {
  const response = await apiClient.post<CreateDatasetResponse>(
    "/api/v1/datasets",
    {
      name,
      dataset_type: datasetType,
    },
    {
      signal,
      timeout: 30000,
    }
  );

  return response.data;
};

export const getDatasets = async (
  page = 1,
  pageSize = 20,
  signal?: AbortSignal
): Promise<DatasetListResponse> => {
  const response = await apiClient.get<DatasetListResponse>(
    "/api/v1/datasets",
    {
      signal,
      timeout: 30000,
      params: {
        page,
        page_size: pageSize,
      },
    }
  );

  return response.data;
};

export const getDataset = async (
  datasetId: string,
  signal?: AbortSignal
): Promise<Dataset> => {
  const response = await apiClient.get<Dataset>(
    `/api/v1/datasets/${datasetId}`,
    {
      signal,
      timeout: 30000,
    }
  );

  return response.data;
};

export const deleteDataset = async (
  datasetId: string
): Promise<void> => {
  await apiClient.delete(`/api/v1/datasets/${datasetId}`);
};

export const uploadDatasetFile = async (
  datasetId: string,
  file: File,
  signal?: AbortSignal
): Promise<UploadDatasetFileResponse> => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.post<UploadDatasetFileResponse>(
    `/api/v1/datasets/${datasetId}/files`,
    formData,
    {
      signal,
      timeout: 120000,
    }
  );

  return response.data;
};

export const getDatasetFile = async (
  datasetId: string,
  fileId: string
): Promise<Blob> => {
  const response = await apiClient.get<Blob>(
    `/api/v1/datasets/${datasetId}/files/${fileId}`,
    {
      responseType: "blob",
    }
  );

  return response.data;
};

export const deleteDatasetFile = async (
  datasetId: string,
  fileId: string
): Promise<void> => {
  await apiClient.delete(
    `/api/v1/datasets/${datasetId}/files/${fileId}`
  );
};