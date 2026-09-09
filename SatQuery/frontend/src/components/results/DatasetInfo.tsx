import type { Dataset, Observation } from "../../types/dataset";

interface DatasetInfoProps {
  dataset: Dataset;
}

const DatasetInfo = ({ dataset }: DatasetInfoProps) => {
  const observation: Observation | undefined =
    dataset.observations[0];

  const raster = observation?.raster;
  const spatial = observation?.spatial;
  const file = observation?.file;
  const source = observation?.source;

  const formatFileSize = (size?: number | null) => {
    if (size == null) {
      return "Unavailable";
    }

    if (size < 1024) {
      return `${size} B`;
    }

    if (size < 1024 * 1024) {
      return `${(size / 1024).toFixed(1)} KB`;
    }

    if (size < 1024 * 1024 * 1024) {
      return `${(size / (1024 * 1024)).toFixed(1)} MB`;
    }

    return `${(size / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  };

  const formatFileType = (mediaType?: string) => {
    if (!mediaType) {
      return "Unavailable";
    }

    const normalizedType = mediaType.toLowerCase();

    if (
      normalizedType === "image/tiff" ||
      normalizedType === "image/geotiff"
    ) {
      return "GeoTIFF";
    }

    if (normalizedType === "image/png") {
      return "PNG";
    }

    if (
      normalizedType === "image/jpeg" ||
      normalizedType === "image/jpg"
    ) {
      return "JPEG";
    }

    return mediaType;
  };

  const formatResolution = (
    resolution?: [number, number] | null
  ) => {
    if (!resolution) {
      return "Unavailable";
    }

    return `${resolution[0]} × ${resolution[1]} m`;
  };

  return (
    <section className="dataset-card">
      <div className="dataset-card-header">
        <div>
          <span className="dataset-label">
            Dataset
          </span>

          <h3>{dataset.name}</h3>
        </div>

        <span
          className={`dataset-status ${dataset.processing.status}`}
        >
          {dataset.processing.status}
        </span>
      </div>

      <div className="dataset-grid">
        <div className="dataset-item">
          <span>Dataset ID</span>

          <strong>
            {dataset.dataset_id}
          </strong>
        </div>

        <div className="dataset-item">
          <span>Dataset type</span>

          <strong>
            {dataset.dataset_type}
          </strong>
        </div>

        <div className="dataset-item">
          <span>File type</span>

          <strong>
            {formatFileType(source?.media_type)}
          </strong>
        </div>

        <div className="dataset-item">
          <span>File size</span>

          <strong>
            {formatFileSize(file?.size)}
          </strong>
        </div>

        <div className="dataset-item">
          <span>Dimensions</span>

          <strong>
            {raster?.width != null &&
            raster?.height != null
              ? `${raster.width} × ${raster.height}`
              : "Unavailable"}
          </strong>
        </div>

        <div className="dataset-item">
          <span>Bands</span>

          <strong>
            {raster?.band_count ?? "Unavailable"}
          </strong>
        </div>

        <div className="dataset-item">
          <span>Resolution</span>

          <strong>
            {formatResolution(
              raster?.resolution
            )}
          </strong>
        </div>

        <div className="dataset-item">
          <span>CRS</span>

          <strong>
            {spatial?.source_crs ||
              spatial?.crs_status ||
              "Unavailable"}
          </strong>
        </div>

        <div className="dataset-item">
          <span>Spatial location</span>

          <strong>
            {spatial?.wgs84_bounds
              ? "Available"
              : "Unavailable"}
          </strong>
        </div>
      </div>

      {!spatial?.wgs84_bounds && (
        <div className="spatial-warning">
          Geographic location is unavailable for this
          dataset.
        </div>
      )}
    </section>
  );
};

export default DatasetInfo;