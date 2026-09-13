export type DatasetType =
  | "single"
  | "temporal"
  | "multimodal";

export type ProcessingStatus =
  | "uploading"
  | "processing"
  | "ready"
  | "failed";

export interface Processing {
  status: ProcessingStatus;
}

export interface Source {
  kind: string;
  locator: string;
  display_name: string;
  media_type: string;
}

export interface Acquisition {
  satellite?: string | null;
  sensor?: string | null;
  acquisition_date?: string | null;
}

export interface NativeBounds {
  west: number;
  south: number;
  east: number;
  north: number;
}

export interface WGS84Bounds {
  west: number;
  south: number;
  east: number;
  north: number;
}

export interface Spatial {
  crs_status: string;
  source_crs?: string | null;
  native_bounds?: NativeBounds | null;
  wgs84_bounds?: WGS84Bounds | null;
  footprint?: unknown | null;
  centroid_wgs84?: [number, number] | null;
  map_ready: boolean;
  map_unavailable_reason?: string | null;
  transform?: unknown | null;
}

export interface RasterBand {
  index: number;
  name: string;
  dtype: string;
  width: number;
  height: number;
  nodata?: number | null;
}

export interface Raster {
  width: number;
  height: number;
  band_count: number;
  bands: RasterBand[];
  dtypes: string[];
  band_names: string[];
  nodata?: number | null;
  resolution?: [number, number] | null;
}

export interface FileReference {
  file_id: string;
  size?: number | null;
  filename?: string | null;
}

export interface Observation {
  source: Source;
  acquisition: Acquisition;
  spatial: Spatial;
  raster: Raster;
  file: FileReference;
}

export interface Dataset {
  dataset_id: string;
  name: string;
  dataset_type: DatasetType;
  processing: Processing;
  observations: Observation[];
}

export interface CreateDatasetResponse {
  dataset_id: string;
  name: string;
  dataset_type: DatasetType;
  processing: Processing;
  observations: Observation[];
}

export interface UploadDatasetFileResponse {
  dataset_id: string;
  file_id: string;
  status: string;
}

export interface DatasetListResponse {
  items: Dataset[];
  page: number;
  page_size: number;
  total: number;
}