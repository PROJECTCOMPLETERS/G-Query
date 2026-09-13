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
  datasetType: DatasetType
): Promise<CreateDatasetResponse> => {
  const response = await apiClient.post<CreateDatasetResponse>(
    "/api/v1/datasets",
    {
      name,
      dataset_type: datasetType,
    }
  );

  return response.data;
};

export const getDatasets = async (
  page = 1,
  pageSize = 20
): Promise<DatasetListResponse> => {
  const response = await apiClient.get<DatasetListResponse>(
    "/api/v1/datasets",
    {
      params: {
        page,
        page_size: pageSize,
      },
    }
  );

  return response.data;
};

export const getDataset = async (
  datasetId: string
): Promise<Dataset> => {
  const response = await apiClient.get<Dataset>(
    `/api/v1/datasets/${datasetId}`
  );

  return response.data;
};

export const deleteDataset = async (
  datasetId: string
): Promise<void> => {
  await apiClient.delete(
    `/api/v1/datasets/${datasetId}`
  );
};

export const uploadDatasetFile = async (
  datasetId: string,
  file: File
): Promise<UploadDatasetFileResponse> => {
  const formData = new FormData();

  formData.append("file", file);

  const response =
    await apiClient.post<UploadDatasetFileResponse>(
      `/api/v1/datasets/${datasetId}/files`,
      formData
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