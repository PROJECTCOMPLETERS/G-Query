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

  dataset_type: "single",

  processing: {
    status: "ready",
  },

  observations: [
    {
      source: {
        kind: "file",
        locator: "demo/chennai_demo.tif",
        display_name: "chennai_demo.tif",
        media_type: "image/tiff",
      },

      acquisition: {
        satellite: "Sentinel-2",
        sensor: "MSI",
        acquisition_date: "2026-01-01",
      },

      spatial: {
        crs_status: "valid",
        source_crs: "EPSG:4326",

        native_bounds: {
          west: DEMO_BOUNDS.min_x,
          south: DEMO_BOUNDS.min_y,
          east: DEMO_BOUNDS.max_x,
          north: DEMO_BOUNDS.max_y,
        },

        wgs84_bounds: {
          west: DEMO_BOUNDS.min_x,
          south: DEMO_BOUNDS.min_y,
          east: DEMO_BOUNDS.max_x,
          north: DEMO_BOUNDS.max_y,
        },

        footprint: null,

        centroid_wgs84: [
          (DEMO_BOUNDS.min_x + DEMO_BOUNDS.max_x) / 2,
          (DEMO_BOUNDS.min_y + DEMO_BOUNDS.max_y) / 2,
        ],

        map_ready: true,

        map_unavailable_reason: null,

        transform: null,
      },

      raster: {
        width: 4096,
        height: 4096,
        band_count: 4,

        bands: [
          {
            index: 1,
            name: "Band 1",
            dtype: "uint16",
            width: 4096,
            height: 4096,
            nodata: null,
          },
          {
            index: 2,
            name: "Band 2",
            dtype: "uint16",
            width: 4096,
            height: 4096,
            nodata: null,
          },
          {
            index: 3,
            name: "Band 3",
            dtype: "uint16",
            width: 4096,
            height: 4096,
            nodata: null,
          },
          {
            index: 4,
            name: "Band 4",
            dtype: "uint16",
            width: 4096,
            height: 4096,
            nodata: null,
          },
        ],

        dtypes: [
          "uint16",
          "uint16",
          "uint16",
          "uint16",
        ],

        band_names: [
          "Band 1",
          "Band 2",
          "Band 3",
          "Band 4",
        ],

        nodata: null,

        resolution: [10, 10],
      },

      file: {
        file_id: "demo_file_001",
        size: 24 * 1024 * 1024,
        filename: "chennai_demo.tif",
      },
    },
  ],
};

/*
 * ============================================================
 * DATASET EXTENT
 * ============================================================
 */

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

/*
 * ============================================================
 * CHANGE AREA
 * ============================================================
 */

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

/*
 * ============================================================
 * FLOOD AREA
 * ============================================================
 */

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

/*
 * ============================================================
 * BUILDINGS
 * ============================================================
 */

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

/*
 * ============================================================
 * ROADS
 * ============================================================
 */

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