export interface SpatialBounds {
  min_x: number;
  min_y: number;
  max_x: number;
  max_y: number;
}

export interface SpatialInformation {
  crs: string | null;
  bounds: SpatialBounds | null;
}

export interface Dataset {
  dataset_id: string;
  name: string;
  format: string;
  file_size?: number;
  width: number | null;
  height: number | null;
  bands: number | null;
  resolution: string | null;
  status: "uploading" | "processing" | "ready" | "failed";
  preview_url?: string | null;
  spatial?: SpatialInformation | null;
}

export interface UploadResponse {
  success: boolean;
  dataset_id: string;
  status: string;
  message?: string;
  dataset?: Dataset;
}

export interface QueryResponse {
  success: boolean;
  answer: string;
  dataset?: Dataset;
  confidence?: number | null;
}

export interface ApiError {
  detail?: string;
  message?: string;
}