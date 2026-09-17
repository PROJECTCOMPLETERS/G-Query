import { useEffect, useRef, useState } from "react";

import * as maplibregl from "maplibre-gl";
import type { Map as MapLibreMap } from "maplibre-gl";

import "maplibre-gl/dist/maplibre-gl.css";

import type { GeoJSONSourceSpecification } from "maplibre-gl";

import type { Dataset } from "../../types/dataset";

import {
  CHANGE_AREA_GEOJSON,
  FLOOD_AREA_GEOJSON,
} from "../data/demoData";

interface MapViewProps {
  dataset: Dataset;
  demoMode?: boolean;
}

interface LayerVisibility {
  dataset: boolean;
  change: boolean;
  flood: boolean;
  buildings: boolean;
  roads: boolean;
}

interface MapBounds {
  west: number;
  south: number;
  east: number;
  north: number;
}

const MapView = ({
  dataset,
  demoMode = false,
}: MapViewProps) => {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MapLibreMap | null>(null);

  const [mapLoaded, setMapLoaded] = useState(false);

  const [layerVisibility, setLayerVisibility] =
    useState<LayerVisibility>({
      dataset: true,
      change: demoMode,
      flood: demoMode,
      buildings: true,
      roads: true,
    });

  /*
   * Backend API URL
   *
   * .env:
   * VITE_API_BASE_URL=http://localhost:8000
   *
   * If .env is not available, localhost:8000 is used.
   */
  const apiBaseUrl =
    import.meta.env.VITE_API_BASE_URL ||
    "http://localhost:8000";

  /*
   * ---------------------------------------------------------
   * DATASET OBSERVATION
   * ---------------------------------------------------------
   */

  const observation = dataset?.observations?.[0];

  const spatial = observation?.spatial;

  /*
   * Dataset WGS84 bounds
   */

  const datasetBounds: MapBounds | null =
    spatial?.wgs84_bounds
      ? {
          west: spatial.wgs84_bounds.west,
          south: spatial.wgs84_bounds.south,
          east: spatial.wgs84_bounds.east,
          north: spatial.wgs84_bounds.north,
        }
      : null;

  /*
   * ---------------------------------------------------------
   * FIT MAP TO DATASET
   * ---------------------------------------------------------
   */

  const fitDataset = () => {
    const map = mapRef.current;

    if (!map || !datasetBounds) {
      return;
    }

    map.fitBounds(
      [
        [datasetBounds.west, datasetBounds.south],
        [datasetBounds.east, datasetBounds.north],
      ],
      {
        padding: 60,
        duration: 1000,
        maxZoom: 16,
      }
    );
  };

  /*
   * ---------------------------------------------------------
   * INITIALIZE MAP
   * ---------------------------------------------------------
   */

  useEffect(() => {
    if (!mapContainerRef.current) {
      return;
    }

    /*
     * Prevent duplicate map initialization
     */

    if (mapRef.current) {
      return;
    }

    /*
     * -------------------------------------------------------
     * SATELLITE BASEMAP
     * -------------------------------------------------------
     */

    const map = new maplibregl.Map({
      container: mapContainerRef.current,

      style: {
        version: 8,

        sources: {
          satellite: {
            type: "raster",

            tiles: [
              "https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-3857/default/g/{z}/{y}/{x}.jpg",
            ],

            tileSize: 256,
            attribution:
              "© EOX IT Services GmbH",
          },
        },

        layers: [
          {
            id: "satellite-layer",

            type: "raster",

            source: "satellite",

            minzoom: 0,
            maxzoom: 19,
          },
        ],
      },

      center: datasetBounds
        ? [
            (datasetBounds.west +
              datasetBounds.east) /
              2,
            (datasetBounds.south +
              datasetBounds.north) /
              2,
          ]
        : [80.22, 13.07],

      zoom: datasetBounds ? 12 : 5,
    });

    mapRef.current = map;

    /*
     * Navigation controls
     */

    map.addControl(
      new maplibregl.NavigationControl(),
      "top-right"
    );

    /*
     * Scale control
     */

    map.addControl(
      new maplibregl.ScaleControl({
        maxWidth: 150,
        unit: "metric",
      }),
      "bottom-left"
    );

    /*
     * -------------------------------------------------------
     * MAP LOAD
     * -------------------------------------------------------
     */

    map.on("load", () => {
      /*
       * =====================================================
       * DATASET EXTENT
       * =====================================================
       */

      if (datasetBounds) {
        const datasetGeoJson: GeoJSONSourceSpecification =
          {
            type: "geojson",

            data: {
              type: "Feature",

              properties: {},

              geometry: {
                type: "Polygon",

                coordinates: [
                  [
                    [
                      datasetBounds.west,
                      datasetBounds.south,
                    ],

                    [
                      datasetBounds.east,
                      datasetBounds.south,
                    ],

                    [
                      datasetBounds.east,
                      datasetBounds.north,
                    ],

                    [
                      datasetBounds.west,
                      datasetBounds.north,
                    ],

                    [
                      datasetBounds.west,
                      datasetBounds.south,
                    ],
                  ],
                ],
              },
            },
          };

        map.addSource(
          "dataset-extent-source",
          datasetGeoJson
        );

        /*
         * Dataset fill
         */

        map.addLayer({
          id: "dataset-extent-fill",

          type: "fill",

          source: "dataset-extent-source",

          paint: {
            "fill-color": "#3b82f6",

            "fill-opacity": 0.08,
          },
        });

        /*
         * Dataset border
         */

        map.addLayer({
          id: "dataset-extent-outline",

          type: "line",

          source: "dataset-extent-source",

          paint: {
            "line-color": "#2563eb",

            "line-width": 2,

            "line-opacity": 0.9,
          },
        });
      }

      /*
       * =====================================================
       * ROADS VECTOR TILE API
       * =====================================================
       *
       * Backend:
       *
       * /api/v1/tiles/roads/{z}/{x}/{y}.pbf
       *
       */

      map.addSource("road-source", {
        type: "vector",

        tiles: [
          `${apiBaseUrl}/api/v1/tiles/roads/{z}/{x}/{y}.pbf`,
        ],

        minzoom: 10,

        maxzoom: 18,
      });

      /*
       * Road layer
       */

      map.addLayer({
        id: "road-line",

        type: "line",

        source: "road-source",

        /*
         * Backend generator is expected to use
         * "roads" as source-layer.
         */

        "source-layer": "roads",

        layout: {
          visibility: layerVisibility.roads
            ? "visible"
            : "none",
        },

        paint: {
          "line-color": "#facc15",

          "line-width": [
            "interpolate",
            ["linear"],
            ["zoom"],

            10,
            1,

            13,
            1.5,

            15,
            3,

            18,
            5,
          ],

          "line-opacity": 0.9,
        },
      });

      /*
       * =====================================================
       * BUILDINGS VECTOR TILE API
       * =====================================================
       *
       * Backend:
       *
       * /api/v1/tiles/buildings/{z}/{x}/{y}.pbf
       *
       */

      map.addSource("building-source", {
        type: "vector",

        tiles: [
          `${apiBaseUrl}/api/v1/tiles/buildings/{z}/{x}/{y}.pbf`,
        ],

        minzoom: 10,

        maxzoom: 18,
      });

      /*
       * Building polygons
       */

      map.addLayer({
        id: "building-fill",

        type: "fill",

        source: "building-source",

        /*
         * Backend generator is expected to use
         * "buildings" as source-layer.
         */

        "source-layer": "buildings",

        layout: {
          visibility: layerVisibility.buildings
            ? "visible"
            : "none",
        },

        paint: {
          "fill-color": "#22c55e",

          "fill-opacity": 0.35,

          "fill-outline-color": "#166534",
        },
      });

      /*
       * =====================================================
       * CHANGE DEMO
       * =====================================================
       */

      if (demoMode) {
        map.addSource(
          "change-source",
          {
            type: "geojson",

            data: CHANGE_AREA_GEOJSON,
          }
        );

        map.addLayer({
          id: "change-fill",

          type: "fill",

          source: "change-source",

          layout: {
            visibility:
              layerVisibility.change
                ? "visible"
                : "none",
          },

          paint: {
            "fill-color": "#ef4444",

            "fill-opacity": 0.45,

            "fill-outline-color":
              "#991b1b",
          },
        });
      }

      /*
       * =====================================================
       * FLOOD DEMO
       * =====================================================
       */

      if (demoMode) {
        map.addSource(
          "flood-source",
          {
            type: "geojson",

            data: FLOOD_AREA_GEOJSON,
          }
        );

        map.addLayer({
          id: "flood-fill",

          type: "fill",

          source: "flood-source",

          layout: {
            visibility:
              layerVisibility.flood
                ? "visible"
                : "none",
          },

          paint: {
            "fill-color": "#06b6d4",

            "fill-opacity": 0.4,

            "fill-outline-color":
              "#0e7490",
          },
        });
      }

      /*
       * =====================================================
       * MAP READY
       * =====================================================
       */

      setMapLoaded(true);

      /*
       * Fit map to dataset
       */

      if (datasetBounds) {
        map.fitBounds(
          [
            [
              datasetBounds.west,
              datasetBounds.south,
            ],

            [
              datasetBounds.east,
              datasetBounds.north,
            ],
          ],
          {
            padding: 60,

            duration: 800,

            maxZoom: 16,
          }
        );
      }
    });

    /*
     * -------------------------------------------------------
     * CLEANUP
     * -------------------------------------------------------
     */

    return () => {
      map.remove();

      mapRef.current = null;

      setMapLoaded(false);
    };

    /*
     * Map should initialize when dataset changes.
     */

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dataset.dataset_id]);

  /*
   * ---------------------------------------------------------
   * LAYER VISIBILITY
   * ---------------------------------------------------------
   */

  useEffect(() => {
    const map = mapRef.current;

    if (!map || !mapLoaded) {
      return;
    }

    /*
     * Dataset
     */

    if (
      map.getLayer("dataset-extent-fill")
    ) {
      map.setLayoutProperty(
        "dataset-extent-fill",
        "visibility",
        layerVisibility.dataset
          ? "visible"
          : "none"
      );
    }

    if (
      map.getLayer("dataset-extent-outline")
    ) {
      map.setLayoutProperty(
        "dataset-extent-outline",
        "visibility",
        layerVisibility.dataset
          ? "visible"
          : "none"
      );
    }

    /*
     * Roads
     */

    if (map.getLayer("road-line")) {
      map.setLayoutProperty(
        "road-line",
        "visibility",
        layerVisibility.roads
          ? "visible"
          : "none"
      );
    }

    /*
     * Buildings
     */

    if (map.getLayer("building-fill")) {
      map.setLayoutProperty(
        "building-fill",
        "visibility",
        layerVisibility.buildings
          ? "visible"
          : "none"
      );
    }

    /*
     * Change
     */

    if (map.getLayer("change-fill")) {
      map.setLayoutProperty(
        "change-fill",
        "visibility",
        layerVisibility.change
          ? "visible"
          : "none"
      );
    }

    /*
     * Flood
     */

    if (map.getLayer("flood-fill")) {
      map.setLayoutProperty(
        "flood-fill",
        "visibility",
        layerVisibility.flood
          ? "visible"
          : "none"
      );
    }
  }, [
    layerVisibility,
    mapLoaded,
  ]);

  /*
   * ---------------------------------------------------------
   * TOGGLE LAYER
   * ---------------------------------------------------------
   */

  const toggleLayer = (
    layer: keyof LayerVisibility
  ) => {
    setLayerVisibility((previous) => ({
      ...previous,

      [layer]: !previous[layer],
    }));
  };

  /*
   * ---------------------------------------------------------
   * RENDER
   * ---------------------------------------------------------
   */

  return (
    <div className="w-full space-y-3">
      {/* =====================================================
          MAP HEADER
          ===================================================== */}

      <div className="flex flex-col gap-3 rounded-lg border bg-white p-4 shadow-sm md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-lg font-semibold">
            Satellite Map
          </h2>

          <p className="text-sm text-gray-500">
            {dataset.name}
          </p>
        </div>

        <button
          type="button"
          onClick={fitDataset}
          disabled={!datasetBounds}
          className="rounded-md bg-black px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          Fit Dataset
        </button>
      </div>

      {/* =====================================================
          LAYER CONTROLS
          ===================================================== */}

      <div className="flex flex-wrap gap-2 rounded-lg border bg-white p-3 shadow-sm">
        {/* Dataset */}

        <button
          type="button"
          onClick={() =>
            toggleLayer("dataset")
          }
          className={`rounded-md border px-3 py-2 text-sm ${
            layerVisibility.dataset
              ? "bg-blue-50 text-blue-700"
              : "bg-gray-50 text-gray-500"
          }`}
        >
          {layerVisibility.dataset
            ? "☑"
            : "☐"}{" "}
          Dataset
        </button>

        {/* Roads */}

        <button
          type="button"
          onClick={() =>
            toggleLayer("roads")
          }
          className={`rounded-md border px-3 py-2 text-sm ${
            layerVisibility.roads
              ? "bg-yellow-50 text-yellow-700"
              : "bg-gray-50 text-gray-500"
          }`}
        >
          {layerVisibility.roads
            ? "☑"
            : "☐"}{" "}
          Roads
        </button>

        {/* Buildings */}

        <button
          type="button"
          onClick={() =>
            toggleLayer("buildings")
          }
          className={`rounded-md border px-3 py-2 text-sm ${
            layerVisibility.buildings
              ? "bg-green-50 text-green-700"
              : "bg-gray-50 text-gray-500"
          }`}
        >
          {layerVisibility.buildings
            ? "☑"
            : "☐"}{" "}
          Buildings
        </button>

        {/* Change */}

        {demoMode && (
          <button
            type="button"
            onClick={() =>
              toggleLayer("change")
            }
            className={`rounded-md border px-3 py-2 text-sm ${
              layerVisibility.change
                ? "bg-red-50 text-red-700"
                : "bg-gray-50 text-gray-500"
            }`}
          >
            {layerVisibility.change
              ? "☑"
              : "☐"}{" "}
            Change
          </button>
        )}

        {/* Flood */}

        {demoMode && (
          <button
            type="button"
            onClick={() =>
              toggleLayer("flood")
            }
            className={`rounded-md border px-3 py-2 text-sm ${
              layerVisibility.flood
                ? "bg-cyan-50 text-cyan-700"
                : "bg-gray-50 text-gray-500"
            }`}
          >
            {layerVisibility.flood
              ? "☑"
              : "☐"}{" "}
            Flood
          </button>
        )}
      </div>

      {/* =====================================================
          MAP
          ===================================================== */}

      <div className="relative h-[600px] w-full overflow-hidden rounded-xl border shadow-sm">
        <div
          ref={mapContainerRef}
          className="h-full w-full"
        />

        {/* Loading */}

        {!mapLoaded && (
          <div className="absolute inset-0 flex items-center justify-center bg-white/70">
            <div className="rounded-lg bg-white px-4 py-3 text-sm shadow">
              Loading map...
            </div>
          </div>
        )}
      </div>

      {/* =====================================================
          DATASET INFORMATION
          ===================================================== */}

      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        {/* Status */}

        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs text-gray-500">
            Processing Status
          </p>

          <p className="mt-1 font-medium capitalize">
            {dataset.processing.status}
          </p>
        </div>

        {/* Raster */}

        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs text-gray-500">
            Raster
          </p>

          <p className="mt-1 font-medium">
            {observation?.raster?.width ?? "-"} ×{" "}
            {observation?.raster?.height ?? "-"}
          </p>
        </div>

        {/* Bands */}

        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs text-gray-500">
            Bands
          </p>

          <p className="mt-1 font-medium">
            {observation?.raster?.band_count ??
              "-"}
          </p>
        </div>
      </div>

      {/* =====================================================
          SPATIAL INFORMATION
          ===================================================== */}

      {spatial && (
        <div className="rounded-lg border bg-white p-4 shadow-sm">
          <h3 className="mb-3 font-semibold">
            Spatial Information
          </h3>

          <div className="grid grid-cols-1 gap-3 text-sm md:grid-cols-2 lg:grid-cols-4">
            <div>
              <p className="text-xs text-gray-500">
                Source CRS
              </p>

              <p className="font-medium">
                {spatial.source_crs || "-"}
              </p>
            </div>

            <div>
              <p className="text-xs text-gray-500">
                Map Ready
              </p>

              <p className="font-medium">
                {spatial.map_ready
                  ? "Yes"
                  : "No"}
              </p>
            </div>

            <div>
              <p className="text-xs text-gray-500">
                West
              </p>

              <p className="font-medium">
                {spatial.wgs84_bounds?.west ??
                  "-"}
              </p>
            </div>

            <div>
              <p className="text-xs text-gray-500">
                East
              </p>

              <p className="font-medium">
                {spatial.wgs84_bounds?.east ??
                  "-"}
              </p>
            </div>

            <div>
              <p className="text-xs text-gray-500">
                South
              </p>

              <p className="font-medium">
                {spatial.wgs84_bounds?.south ??
                  "-"}
              </p>
            </div>

            <div>
              <p className="text-xs text-gray-500">
                North
              </p>

              <p className="font-medium">
                {spatial.wgs84_bounds?.north ??
                  "-"}
              </p>
            </div>

            <div>
              <p className="text-xs text-gray-500">
                Resolution
              </p>

              <p className="font-medium">
                {observation?.raster?.resolution
                  ? `${observation.raster.resolution[0]} × ${observation.raster.resolution[1]}`
                  : "-"}
              </p>
            </div>

            <div>
              <p className="text-xs text-gray-500">
                Band Count
              </p>

              <p className="font-medium">
                {observation?.raster
                  ?.band_count ?? "-"}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* =====================================================
          BAND INFORMATION
          ===================================================== */}

      {observation?.raster?.bands &&
        observation.raster.bands.length > 0 && (
          <div className="rounded-lg border bg-white p-4 shadow-sm">
            <h3 className="mb-3 font-semibold">
              Raster Bands
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full min-w-[600px] text-left text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="px-3 py-2">
                      Index
                    </th>

                    <th className="px-3 py-2">
                      Band
                    </th>

                    <th className="px-3 py-2">
                      Data Type
                    </th>

                    <th className="px-3 py-2">
                      Width
                    </th>

                    <th className="px-3 py-2">
                      Height
                    </th>

                    <th className="px-3 py-2">
                      NoData
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {observation.raster.bands.map(
                    (band) => (
                      <tr
                        key={band.index}
                        className="border-b last:border-b-0"
                      >
                        <td className="px-3 py-2">
                          {band.index}
                        </td>

                        <td className="px-3 py-2 font-medium">
                          {band.name}
                        </td>

                        <td className="px-3 py-2">
                          {band.dtype}
                        </td>

                        <td className="px-3 py-2">
                          {band.width}
                        </td>

                        <td className="px-3 py-2">
                          {band.height}
                        </td>

                        <td className="px-3 py-2">
                          {band.nodata ?? "-"}
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
    </div>
  );
};

export default MapView;