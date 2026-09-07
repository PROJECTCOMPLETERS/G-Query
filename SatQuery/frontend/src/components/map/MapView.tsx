import { useEffect, useRef, useState } from "react";

import * as maplibregl from "maplibre-gl";
import type { GeoJSONSourceSpecification } from "maplibre-gl";

import "maplibre-gl/dist/maplibre-gl.css";

import {
  BUILDINGS_GEOJSON,
  CHANGE_AREA_GEOJSON,
  FLOOD_AREA_GEOJSON,
  ROADS_GEOJSON,
} from "../data/demoData";

import type {
  SpatialBounds,
  SpatialInformation,
} from "../../types/dataset";

interface MapViewProps {
  spatial?: SpatialInformation | null;
  demoMode?: boolean;
}

interface LayerVisibility {
  dataset: boolean;
  change: boolean;
  flood: boolean;
  buildings: boolean;
  roads: boolean;
}

const isValidBounds = (
  value?: SpatialBounds | null
): value is SpatialBounds => {
  if (!value) return false;

  return [
    value.min_x,
    value.min_y,
    value.max_x,
    value.max_y,
  ].every(Number.isFinite);
};

const createDatasetGeoJSON = (
  datasetBounds: SpatialBounds
) => ({
  type: "FeatureCollection",

  features: [
    {
      type: "Feature",

      properties: {
        name: "Dataset Geographic Extent",
      },

      geometry: {
        type: "Polygon",

        coordinates: [
          [
            [
              datasetBounds.min_x,
              datasetBounds.min_y,
            ],

            [
              datasetBounds.max_x,
              datasetBounds.min_y,
            ],

            [
              datasetBounds.max_x,
              datasetBounds.max_y,
            ],

            [
              datasetBounds.min_x,
              datasetBounds.max_y,
            ],

            [
              datasetBounds.min_x,
              datasetBounds.min_y,
            ],
          ],
        ],
      },
    },
  ],
});

const MapView = ({
  spatial,
  demoMode = false,
}: MapViewProps) => {
  const mapContainerRef =
    useRef<HTMLDivElement>(null);

  const mapRef = useRef<maplibregl.Map | null>(
    null
  );

  const [mapLoaded, setMapLoaded] = useState(false);

  const [layers, setLayers] =
    useState<LayerVisibility>({
      dataset: true,
      change: true,
      flood: false,
      buildings: true,
      roads: true,
    });

  const bounds = spatial?.bounds;

  const fitDataset = () => {
    const map = mapRef.current;

    if (!map || !isValidBounds(bounds)) return;

    map.fitBounds(
      [
        [bounds.min_x, bounds.min_y],
        [bounds.max_x, bounds.max_y],
      ],

      {
        padding: 55,
        duration: 900,
      }
    );
  };

  const setMapLayerVisibility = (
    layerIds: string[],
    visible: boolean
  ) => {
    const map = mapRef.current;

    if (!map || !mapLoaded) return;

    layerIds.forEach((layerId) => {
      if (map.getLayer(layerId)) {
        map.setLayoutProperty(
          layerId,
          "visibility",
          visible ? "visible" : "none"
        );
      }
    });
  };

  const toggleLayer = (
    layerName: keyof LayerVisibility
  ) => {
    const nextValue = !layers[layerName];

    setLayers((currentLayers) => ({
      ...currentLayers,
      [layerName]: nextValue,
    }));

    const layerIds: Record<
      keyof LayerVisibility,
      string[]
    > = {
      dataset: [
        "dataset-fill",
        "dataset-outline",
      ],

      change: ["change-area"],

      flood: ["flood-area"],

      buildings: ["building-points"],

      roads: ["road-line"],
    };

    setMapLayerVisibility(
      layerIds[layerName],
      nextValue
    );
  };

  useEffect(() => {
    if (
      !mapContainerRef.current ||
      !isValidBounds(bounds)
    ) {
      return;
    }

    const centerLongitude =
      (bounds.min_x + bounds.max_x) / 2;

    const centerLatitude =
      (bounds.min_y + bounds.max_y) / 2;

    const map = new maplibregl.Map({
      container: mapContainerRef.current,

      /*
       * Sentinel-2 satellite raster basemap
       */
      style: {
        version: 8,

        sources: {
          satellite: {
            type: "raster",

            tiles: [
              "https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/default/g/{z}/{y}/{x}.jpg",
            ],

            tileSize: 256,

            attribution:
              "Sentinel-2 cloudless imagery by EOX",
          },
        },

        layers: [
          {
            id: "satellite-basemap",
            type: "raster",
            source: "satellite",

            paint: {
              "raster-opacity": 1,
              "raster-saturation": 0.1,
              "raster-contrast": 0.08,
            },
          },
        ],
      },

      center: [
        centerLongitude,
        centerLatitude,
      ],

      zoom: 10,
    });

    mapRef.current = map;

    /*
     * Zoom, compass and map rotation controls
     */
    map.addControl(
      new maplibregl.NavigationControl({
        showCompass: true,
        showZoom: true,
      }),

      "top-right"
    );

    /*
     * Map scale
     */
    map.addControl(
      new maplibregl.ScaleControl({
        maxWidth: 120,
        unit: "metric",
      }),

      "bottom-left"
    );

    map.on("load", () => {
      /*
       * Dataset geographic extent
       */
      const datasetGeoJSON =
        createDatasetGeoJSON(bounds);

      map.addSource("dataset-source", {
        type: "geojson",

        data:
          datasetGeoJSON as GeoJSONSourceSpecification["data"],
      });

      map.addLayer({
        id: "dataset-fill",
        type: "fill",
        source: "dataset-source",

        layout: {
          visibility: "visible",
        },

        paint: {
          "fill-color": "#38bdf8",
          "fill-opacity": 0.14,
        },
      });

      map.addLayer({
        id: "dataset-outline",
        type: "line",
        source: "dataset-source",

        layout: {
          visibility: "visible",
        },

        paint: {
          "line-color": "#38bdf8",
          "line-width": 3,
          "line-dasharray": [2, 2],
        },
      });

      /*
       * Demo change-detection layer
       */
      map.addSource("change-source", {
        type: "geojson",

        data:
          CHANGE_AREA_GEOJSON as GeoJSONSourceSpecification["data"],
      });

      map.addLayer({
        id: "change-area",
        type: "fill",
        source: "change-source",

        layout: {
          visibility: "visible",
        },

        paint: {
          "fill-color": "#f97316",
          "fill-opacity": 0.35,
          "fill-outline-color": "#fb923c",
        },
      });

      /*
       * Demo flood layer
       */
      map.addSource("flood-source", {
        type: "geojson",

        data:
          FLOOD_AREA_GEOJSON as GeoJSONSourceSpecification["data"],
      });

      map.addLayer({
        id: "flood-area",
        type: "fill",
        source: "flood-source",

        layout: {
          visibility: "none",
        },

        paint: {
          "fill-color": "#2563eb",
          "fill-opacity": 0.45,
          "fill-outline-color": "#60a5fa",
        },
      });

      /*
       * Demo buildings layer
       */
      map.addSource("building-source", {
        type: "geojson",

        data:
          BUILDINGS_GEOJSON as GeoJSONSourceSpecification["data"],
      });

      map.addLayer({
        id: "building-points",
        type: "circle",
        source: "building-source",

        layout: {
          visibility: "visible",
        },

        paint: {
          "circle-radius": 7,
          "circle-color": "#22c55e",
          "circle-stroke-color": "#ffffff",
          "circle-stroke-width": 2,
        },
      });

      /*
       * Demo road layer
       */
      map.addSource("road-source", {
        type: "geojson",

        data:
          ROADS_GEOJSON as GeoJSONSourceSpecification["data"],
      });

      map.addLayer({
        id: "road-line",
        type: "line",
        source: "road-source",

        layout: {
          visibility: "visible",
        },

        paint: {
          "line-color": "#facc15",
          "line-width": 4,
        },
      });

      setMapLoaded(true);

      /*
       * Automatic dataset location focus
       */
      map.fitBounds(
        [
          [bounds.min_x, bounds.min_y],
          [bounds.max_x, bounds.max_y],
        ],

        {
          padding: 55,
          duration: 0,
        }
      );
    });

    return () => {
      setMapLoaded(false);

      map.remove();

      mapRef.current = null;
    };
  }, [bounds]);

  /*
   * Spatial information missing fallback
   */
  if (!isValidBounds(bounds)) {
    return (
      <section className="map-fallback">
        <strong>Map unavailable</strong>

        <p>
          Geographic location is unavailable for this
          dataset.
        </p>
      </section>
    );
  }

  return (
    <section className="map-card">
      <div className="map-card-header">
        <div>
          <div className="map-title-row">
            <h3>Interactive Satellite Map</h3>

            {demoMode && (
              <span className="demo-badge">
                Demo Data
              </span>
            )}
          </div>

          <p>
            Explore the satellite basemap, dataset extent
            and visualization layers.
          </p>
        </div>

        <button
          type="button"
          className="fit-dataset-btn"
          onClick={fitDataset}
          disabled={!mapLoaded}
        >
          Fit Dataset
        </button>
      </div>

      <div className="map-layout">
        <div className="map-wrapper">
          {!mapLoaded && (
            <div className="map-loading">
              Loading satellite map...
            </div>
          )}

          <div
            ref={mapContainerRef}
            className="map-view"
          />
        </div>

        <aside className="layer-panel">
          <h4>Map Layers</h4>

          <label>
            <input
              type="checkbox"
              checked={layers.dataset}
              onChange={() =>
                toggleLayer("dataset")
              }
            />

            <span className="layer-color dataset" />

            Dataset extent
          </label>

          <label>
            <input
              type="checkbox"
              checked={layers.change}
              onChange={() =>
                toggleLayer("change")
              }
            />

            <span className="layer-color change" />

            Change area
          </label>

          <label>
            <input
              type="checkbox"
              checked={layers.flood}
              onChange={() =>
                toggleLayer("flood")
              }
            />

            <span className="layer-color flood" />

            Flood area
          </label>

          <label>
            <input
              type="checkbox"
              checked={layers.buildings}
              onChange={() =>
                toggleLayer("buildings")
              }
            />

            <span className="layer-color buildings" />

            Buildings
          </label>

          <label>
            <input
              type="checkbox"
              checked={layers.roads}
              onChange={() =>
                toggleLayer("roads")
              }
            />

            <span className="layer-color roads" />

            Roads
          </label>
        </aside>
      </div>

      <div className="map-metadata">
        <div>
          <span>CRS</span>

          <strong>
            {spatial?.crs || "Unavailable"}
          </strong>
        </div>

        <div>
          <span>Minimum coordinates</span>

          <strong>
            {bounds.min_x.toFixed(4)},{" "}
            {bounds.min_y.toFixed(4)}
          </strong>
        </div>

        <div>
          <span>Maximum coordinates</span>

          <strong>
            {bounds.max_x.toFixed(4)},{" "}
            {bounds.max_y.toFixed(4)}
          </strong>
        </div>
      </div>
    </section>
  );
};

export default MapView;