import type { Dataset } from "../../types/dataset";

export const DEMO_BOUNDS = {
  min_x: 80.20,
  min_y: 12.90,
  max_x: 80.35,
  max_y: 13.15,
};

export const DEMO_DATASET: Dataset = {
  dataset_id: "demo_chennai_001",
  name: "chennai_demo.tif",
  format: "GeoTIFF",
  file_size: 24 * 1024 * 1024,
  width: 4096,
  height: 4096,
  bands: 4,
  resolution: "10m",
  status: "ready",
  preview_url: null,

  spatial: {
    crs: "EPSG:4326",
    bounds: DEMO_BOUNDS,
  },
};

export const DATASET_EXTENT_GEOJSON = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: {
        name: "Dataset Extent",
        layerType: "dataset",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [DEMO_BOUNDS.min_x, DEMO_BOUNDS.min_y],
            [DEMO_BOUNDS.max_x, DEMO_BOUNDS.min_y],
            [DEMO_BOUNDS.max_x, DEMO_BOUNDS.max_y],
            [DEMO_BOUNDS.min_x, DEMO_BOUNDS.max_y],
            [DEMO_BOUNDS.min_x, DEMO_BOUNDS.min_y],
          ],
        ],
      },
    },
  ],
};

export const CHANGE_AREA_GEOJSON = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: {
        name: "Demo Change Area",
        layerType: "change",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [80.245, 12.97],
            [80.315, 12.97],
            [80.315, 13.07],
            [80.245, 13.07],
            [80.245, 12.97],
          ],
        ],
      },
    },
  ],
};

export const FLOOD_AREA_GEOJSON = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: {
        name: "Demo Flood Area",
        layerType: "flood",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [80.27, 12.93],
            [80.335, 12.93],
            [80.335, 12.985],
            [80.27, 12.985],
            [80.27, 12.93],
          ],
        ],
      },
    },
  ],
};

export const BUILDINGS_GEOJSON = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: {
        name: "Demo Building 1",
      },
      geometry: {
        type: "Point",
        coordinates: [80.255, 13.04],
      },
    },
    {
      type: "Feature",
      properties: {
        name: "Demo Building 2",
      },
      geometry: {
        type: "Point",
        coordinates: [80.29, 13.075],
      },
    },
    {
      type: "Feature",
      properties: {
        name: "Demo Building 3",
      },
      geometry: {
        type: "Point",
        coordinates: [80.32, 13.025],
      },
    },
  ],
};

export const ROADS_GEOJSON = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: {
        name: "Demo Road",
      },
      geometry: {
        type: "LineString",
        coordinates: [
          [80.215, 12.94],
          [80.25, 12.98],
          [80.28, 13.01],
          [80.31, 13.06],
          [80.34, 13.11],
        ],
      },
    },
  ],
};