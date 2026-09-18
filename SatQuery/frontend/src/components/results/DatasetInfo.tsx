import { useId, useState } from 'react';
import './DatasetInfo.css';

interface Props {
  dataset: unknown;
}

type DataObject = Record<string, unknown>;
type View = 'overview' | 'observations' | 'json';

function asObject(value: unknown): DataObject {
  if (
    value !== null &&
    typeof value === 'object' &&
    !Array.isArray(value)
  ) {
    return value as DataObject;
  }

  return {};
}

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

// Supports a direct dataset or common API response envelopes.
function unwrapDataset(value: unknown): DataObject {
  const root = asObject(value);
  const data = asObject(root.data);

  const candidates = [
    root,
    asObject(root.dataset),
    data,
    asObject(data.dataset),
  ];

  return (
    candidates.find(
      item =>
        'observations' in item ||
        'dataset_id' in item ||
        '_id' in item
    ) || root
  );
}

function jsonText(value: unknown): string {
  try {
    return JSON.stringify(value, null, 2) ?? 'null';
  } catch {
    return 'This value could not be displayed as JSON.';
  }
}

// Also supports MongoDB Extended JSON values.
function displayValue(value: unknown): string {
  if (value === null || value === undefined || value === '') {
    return 'Not provided';
  }

  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No';
  }

  if (typeof value === 'string' || typeof value === 'number') {
    return String(value);
  }

  if (Array.isArray(value)) {
    return value.length
      ? value.map(displayValue).join(', ')
      : 'None';
  }

  const object = asObject(value);

  for (const key of [
    '$oid',
    '$numberInt',
    '$numberLong',
    '$numberDouble',
    '$numberDecimal',
    '$date',
  ]) {
    if (key in object) {
      return displayValue(object[key]);
    }
  }

  return jsonText(value);
}

function fileSize(value: unknown): string {
  if (value === null || value === undefined) {
    return 'Not provided';
  }

  const bytes = Number(displayValue(value));

  if (!Number.isFinite(bytes) || bytes < 0) {
    return displayValue(value);
  }

  return (
    `${(bytes / (1024 * 1024)).toFixed(2)} MiB` +
    ` (${bytes.toLocaleString('en-US')} bytes)`
  );
}

function Fields({
  items,
}: {
  items: Array<[string, unknown]>;
}) {
  return (
    <dl className="ds-fields">
      {items.map(([label, value]) => (
        <div className="ds-field" key={label}>
          <dt>{label}</dt>
          <dd>{displayValue(value)}</dd>
        </div>
      ))}
    </dl>
  );
}

function JsonBlock({ value }: { value: unknown }) {
  return (
    <pre className="ds-json">
      <code>{jsonText(value)}</code>
    </pre>
  );
}

function Bounds({
  title,
  value,
}: {
  title: string;
  value: unknown;
}) {
  const bounds = asObject(value);

  return (
    <section className="ds-section">
      <h4>{title}</h4>

      <Fields
        items={[
          ['West', bounds.west],
          ['South', bounds.south],
          ['East', bounds.east],
          ['North', bounds.north],
        ]}
      />
    </section>
  );
}

function ObservationDetails({
  observation,
  index,
}: {
  observation: DataObject;
  index: number;
}) {
  const source = asObject(observation.source);
  const acquisition = asObject(observation.acquisition);
  const spatial = asObject(observation.spatial);
  const raster = asObject(observation.raster);
  const file = asObject(observation.file);
  const transform = asObject(spatial.transform);

  const bands = asArray(raster.bands).map(asObject);

  const filename =
    file.filename ||
    source.display_name ||
    `Observation ${index + 1}`;

  return (
    <details className="ds-observation" open={index === 0}>
      <summary>
        <span>
          <strong>{displayValue(filename)}</strong>
          <small>Observation {index + 1}</small>
        </span>

        <span className="ds-file-type">
          {displayValue(file.input_kind || source.media_type)}
        </span>
      </summary>

      <div className="ds-observation-body">
        <section className="ds-section">
          <h4>File and source</h4>

          <Fields
            items={[
              ['Observation ID', observation.observation_id],
              ['File ID', file.file_id],
              ['Filename', file.filename],
              ['File size', fileSize(file.size_bytes)],
              ['Input kind', file.input_kind],
              ['Driver', file.driver],
              ['File media type', file.media_type],
              ['Source kind', source.kind],
              ['Source locator', source.locator],
              ['Source display name', source.display_name],
              ['Source media type', source.media_type],
              ['Acquisition datetime', acquisition.datetime],
            ]}
          />
        </section>

        <section className="ds-section">
          <h4>Spatial information</h4>

          <Fields
            items={[
              ['CRS status', spatial.crs_status],
              ['Source CRS', spatial.source_crs],
              ['Map ready', spatial.map_ready],
              [
                'Map unavailable reason',
                spatial.map_unavailable_reason,
              ],
              ['Centroid WGS84 [longitude, latitude]', spatial.centroid_wgs84],
            ]}
          />
        </section>

        <Bounds
          title="Native bounds"
          value={spatial.native_bounds}
        />

        <Bounds
          title="WGS84 bounds"
          value={spatial.wgs84_bounds}
        />

        <section className="ds-section">
          <h4>Raster information</h4>

          <Fields
            items={[
              ['Width in pixels', raster.width],
              ['Height in pixels', raster.height],
              ['Band count', raster.band_count],
              ['Band names', raster.band_names],
              ['Data types', raster.dtypes],
              ['No-data value', raster.nodata],
              ['Resolution [x, y]', raster.resolution],
            ]}
          />
        </section>

        <section className="ds-section">
          <h4>Bands ({bands.length})</h4>

          {bands.length > 0 ? (
            <div
              className="ds-table-scroll"
              role="region"
              aria-label={`Bands for ${displayValue(filename)}`}
              tabIndex={0}
            >
              <table className="ds-bands-table">
                <thead>
                  <tr>
                    <th scope="col">Index</th>
                    <th scope="col">Name</th>
                    <th scope="col">Data type</th>
                    <th scope="col">Width</th>
                    <th scope="col">Height</th>
                    <th scope="col">No-data</th>
                  </tr>
                </thead>

                <tbody>
                  {bands.map((band, bandIndex) => (
                    <tr key={bandIndex}>
                      <td>{displayValue(band.index)}</td>
                      <td>{displayValue(band.name)}</td>
                      <td>{displayValue(band.dtype)}</td>
                      <td>{displayValue(band.width)}</td>
                      <td>{displayValue(band.height)}</td>
                      <td>{displayValue(band.nodata)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="ds-muted">
              Band metadata was not provided.
            </p>
          )}
        </section>

        <section className="ds-section">
          <h4>Affine transform</h4>

          <Fields
            items={[
              ['a', transform.a],
              ['b', transform.b],
              ['c', transform.c],
              ['d', transform.d],
              ['e', transform.e],
              ['f', transform.f],
            ]}
          />
        </section>

        <section className="ds-section">
          <h4>Footprint GeoJSON</h4>

          {spatial.footprint_geojson == null ? (
            <p className="ds-muted">Not provided</p>
          ) : (
            <JsonBlock value={spatial.footprint_geojson} />
          )}
        </section>

        <section className="ds-section">
          <h4>File tags</h4>

          {file.tags == null ? (
            <p className="ds-muted">Not provided</p>
          ) : (
            <JsonBlock value={file.tags} />
          )}
        </section>
      </div>
    </details>
  );
}

export default function DatasetInfo({ dataset }: Props) {
  const [view, setView] = useState<View>('overview');
  const [copyStatus, setCopyStatus] = useState('');

  const instanceId = useId();

  const data = unwrapDataset(dataset);
  const processing = asObject(data.processing);
  const observations = asArray(data.observations).map(asObject);

  const datasetId = data.dataset_id ?? data._id;
  const status = displayValue(processing.status);
  const rawJson = jsonText(data);

  async function copyJson() {
    try {
      await navigator.clipboard.writeText(rawJson);
      setCopyStatus('Dataset JSON copied.');
    } catch {
      setCopyStatus(
        'Copy unavailable. Open Full JSON and select the text to copy.'
      );
    }
  }

  if (Object.keys(data).length === 0) {
    return (
      <section className="ds-details-card">
        <p className="ds-muted">
          Dataset metadata has not been received yet.
        </p>
      </section>
    );
  }

  return (
    <section
      className="ds-details-card"
      aria-labelledby={`${instanceId}-title`}
    >
      <header className="ds-header">
        <div>
          <span className="ds-eyebrow">Dataset information</span>

          <h3 id={`${instanceId}-title`}>
            {data.name ? displayValue(data.name) : 'Dataset details'}
          </h3>

          <p className="ds-subtitle">
            {observations.length}{' '}
            {observations.length === 1
              ? 'observation'
              : 'observations'}
            {' · '}
            {displayValue(data.dataset_type)}
          </p>
        </div>

        <span
          className="ds-status"
          data-status={status.toLowerCase()}
        >
          {status}
        </span>
      </header>

      <div
        className="ds-view-buttons"
        role="group"
        aria-label="Dataset detail views"
      >
        <button
          type="button"
          aria-pressed={view === 'overview'}
          onClick={() => setView('overview')}
        >
          Overview
        </button>

        <button
          type="button"
          aria-pressed={view === 'observations'}
          onClick={() => setView('observations')}
        >
          Observations ({observations.length})
        </button>

        <button
          type="button"
          aria-pressed={view === 'json'}
          onClick={() => setView('json')}
        >
          Full JSON
        </button>
      </div>

      <div className="ds-content">
        {view === 'overview' && (
          <>
            <Fields
              items={[
                ['Dataset ID', datasetId],
                ['Dataset name', data.name],
                ['Dataset type', data.dataset_type],
                ['Processing status', processing.status],
                ['Observation count', observations.length],
              ]}
            />

            {observations.length > 0 && (
              <section className="ds-section">
                <h4>Files in this dataset</h4>

                <div className="ds-file-list">
                  {observations.map((observation, index) => {
                    const file = asObject(observation.file);
                    const source = asObject(observation.source);
                    const spatial = asObject(observation.spatial);

                    return (
                      <div className="ds-file-summary" key={index}>
                        <strong>
                          {displayValue(
                            file.filename ||
                              source.display_name ||
                              `Observation ${index + 1}`
                          )}
                        </strong>

                        <span>{fileSize(file.size_bytes)}</span>

                        <span>
                          CRS: {displayValue(spatial.source_crs)}
                        </span>

                        <span>
                          Map ready: {displayValue(spatial.map_ready)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </section>
            )}
          </>
        )}

        {view === 'observations' && (
          <>
            {observations.length === 0 ? (
              <p className="ds-muted">
                No observations were returned by the backend.
              </p>
            ) : (
              observations.map((observation, index) => (
                <ObservationDetails
                  key={`${displayValue(
                    observation.observation_id
                  )}-${index}`}
                  observation={observation}
                  index={index}
                />
              ))
            )}
          </>
        )}

        {view === 'json' && (
          <>
            <div className="ds-json-toolbar">
              <span>Complete dataset response</span>

              <button
                type="button"
                onClick={() => void copyJson()}
              >
                Copy JSON
              </button>
            </div>

            <pre className="ds-json ds-full-json">
              <code>{rawJson}</code>
            </pre>
          </>
        )}

        {copyStatus && (
          <p className="ds-copy-status" role="status">
            {copyStatus}
          </p>
        )}
      </div>
    </section>
  );
}