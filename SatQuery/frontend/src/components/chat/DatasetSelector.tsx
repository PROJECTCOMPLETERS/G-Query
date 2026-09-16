import { useEffect, useState } from "react";
import { getDatasets } from "../../api/datasetApi";

import type {
  Dataset,
  DatasetType,
} from "../../types/dataset";

interface Props {
  dataset?: Dataset;
  ids: string[];
  busy: boolean;
  uploadType: DatasetType;

  onUploadType: (type: DatasetType) => void;

  onChange: (
    dataset: Dataset | undefined,
    ids: string[]
  ) => void;
}

export default function DatasetSelector({
  dataset,
  ids,
  busy,
  uploadType,
  onUploadType,
  onChange,
}: Props) {
  const [items, setItems] = useState<Dataset[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [version, setVersion] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    setLoading(true);
    setError("");

    getDatasets(page, 20, controller.signal)
      .then((result) => {
        setItems(result.items);
        setTotal(result.total);
      })
      .catch(() => {
        if (!controller.signal.aborted) {
          setError(
            "Could not load datasets. Check your backend connection."
          );
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      });

    return () => controller.abort();
  }, [page, version]);

  return (
    <div className="dataset-selector">
      <label>
        Dataset

        <select
          value={dataset?.dataset_id || ""}
          disabled={busy || loading}
          onChange={(event) => {
            const selected = items.find(
              (item) =>
                item.dataset_id === event.target.value
            );

            onChange(
              selected,
              selected?.observations.map(
                (observation) => observation.observation_id
              ) || []
            );
          }}
        >
          <option value="">New upload / no dataset</option>

          {dataset &&
            !items.some(
              (item) => item.dataset_id === dataset.dataset_id
            ) && (
              <option value={dataset.dataset_id}>
                {dataset.name}
              </option>
            )}

          {items.map((item) => (
            <option
              key={item.dataset_id}
              value={item.dataset_id}
            >
              {item.name}
            </option>
          ))}
        </select>
      </label>

      <div className="dataset-paging">
        <button
          disabled={busy || loading || page === 1}
          onClick={() => setPage((value) => value - 1)}
        >
          Previous
        </button>

        <span>Page {page}</span>

        <button
          disabled={busy || loading || page * 20 >= total}
          onClick={() => setPage((value) => value + 1)}
        >
          Next
        </button>

        <button
          disabled={busy || loading}
          onClick={() => setVersion((value) => value + 1)}
        >
          Refresh
        </button>
      </div>

      {loading && <p role="status">Loading datasets…</p>}
      {error && <p role="alert">{error}</p>}

      {!dataset && (
        <label>
          New dataset type

          <select
            value={uploadType}
            disabled={busy}
            onChange={(event) =>
              onUploadType(event.target.value as DatasetType)
            }
          >
            <option value="single">Single image</option>
            <option value="temporal">Temporal observations</option>
            <option value="multimodal">Multimodal observations</option>
          </select>
        </label>
      )}

      {dataset && (
        <fieldset>
          <legend>Observations</legend>

          {dataset.observations.map((observation) => (
            <label key={observation.observation_id}>
              <input
                type="checkbox"
                disabled={busy}
                checked={ids.includes(
                  observation.observation_id
                )}
                onChange={(event) =>
                  onChange(
                    dataset,
                    event.target.checked
                      ? [...ids, observation.observation_id]
                      : ids.filter(
                          (id) =>
                            id !== observation.observation_id
                        )
                  )
                }
              />

              {observation.source.display_name ||
                observation.observation_id}
            </label>
          ))}
        </fieldset>
      )}

      <small>
        Uploads are added to the selected dataset.
        The Data Engine checks compatibility.
      </small>
    </div>
  );
}