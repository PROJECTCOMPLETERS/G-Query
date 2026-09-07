import type { Dataset } from "../../types/dataset";

interface DatasetInfoProps {
  dataset: Dataset;
}

const DatasetInfo = ({
  dataset,
}: DatasetInfoProps) => {
  const formatFileSize = (size?: number) => {
    if (!size) return "Unavailable";

    if (size < 1024 * 1024) {
      return `${(size / 1024).toFixed(1)} KB`;
    }

    return `${(size / (1024 * 1024)).toFixed(
      1
    )} MB`;
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
          className={`dataset-status ${dataset.status}`}
        >
          {dataset.status}
        </span>
      </div>

      <div className="dataset-grid">
        <div className="dataset-item">
          <span>Dataset ID</span>
          <strong>{dataset.dataset_id}</strong>
        </div>

        <div className="dataset-item">
          <span>Format</span>
          <strong>{dataset.format}</strong>
        </div>

        <div className="dataset-item">
          <span>File size</span>
          <strong>
            {formatFileSize(dataset.file_size)}
          </strong>
        </div>

        <div className="dataset-item">
          <span>Dimensions</span>
          <strong>
            {dataset.width && dataset.height
              ? `${dataset.width} × ${dataset.height}`
              : "Unavailable"}
          </strong>
        </div>

        <div className="dataset-item">
          <span>Bands</span>
          <strong>
            {dataset.bands ?? "Unavailable"}
          </strong>
        </div>

        <div className="dataset-item">
          <span>Resolution</span>
          <strong>
            {dataset.resolution || "Unavailable"}
          </strong>
        </div>

        <div className="dataset-item">
          <span>CRS</span>
          <strong>
            {dataset.spatial?.crs ||
              "Unavailable"}
          </strong>
        </div>

        <div className="dataset-item">
          <span>Spatial location</span>
          <strong>
            {dataset.spatial?.bounds
              ? "Available"
              : "Unavailable"}
          </strong>
        </div>
      </div>

      {!dataset.spatial?.bounds && (
        <div className="spatial-warning">
          Geographic location is unavailable for this
          dataset.
        </div>
      )}
    </section>
  );
};

export default DatasetInfo;