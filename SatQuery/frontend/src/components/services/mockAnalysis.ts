import { DEMO_DATASET } from "../data/demoData";

import type {
  Dataset,
  QueryResponse,
} from "../../types/dataset";

const wait = (milliseconds: number) =>
  new Promise((resolve) =>
    window.setTimeout(resolve, milliseconds)
  );

const getFileFormat = (file?: File | null) => {
  if (!file) return "GeoTIFF";

  const extension = file.name
    .split(".")
    .pop()
    ?.toLowerCase();

  if (extension === "png") return "PNG";

  if (
    extension === "jpg" ||
    extension === "jpeg"
  ) {
    return "JPEG";
  }

  if (
    extension === "tif" ||
    extension === "tiff"
  ) {
    return "GeoTIFF";
  }

  return extension?.toUpperCase() || "Unknown";
};

const createDemoDataset = (
  file?: File | null
): Dataset => {
  return {
    ...DEMO_DATASET,

    name: file?.name || DEMO_DATASET.name,

    format: getFileFormat(file),

    file_size:
      file?.size || DEMO_DATASET.file_size,

    spatial: DEMO_DATASET.spatial
      ? {
          ...DEMO_DATASET.spatial,

          bounds: DEMO_DATASET.spatial.bounds
            ? {
                ...DEMO_DATASET.spatial.bounds,
              }
            : null,
        }
      : null,
  };
};

const generateRelatedAnswer = (
  query: string,
  hasFile: boolean
) => {
  const normalizedQuery = query.toLowerCase();

  if (
    normalizedQuery.includes("flood") ||
    normalizedQuery.includes("water")
  ) {
    return `
Demo analysis indicates possible water-covered or flood-affected regions inside the highlighted dataset boundary.

Low-lying areas near water channels appear to have the highest potential impact. The blue layer on the map represents a sample flood visualization.

This is built-in demonstration data and not a real satellite flood assessment.
    `.trim();
  }

  if (
    normalizedQuery.includes("building") ||
    normalizedQuery.includes("urban") ||
    normalizedQuery.includes("built")
  ) {
    return `
Demo analysis indicates multiple built-up locations within the selected geographic extent.

The building markers represent sample detected structures. This visualization demonstrates how future model-generated building results can be displayed on the map.

This is built-in demonstration data and not a real building-detection result.
    `.trim();
  }

  if (
    normalizedQuery.includes("road") ||
    normalizedQuery.includes("transport")
  ) {
    return `
Demo analysis indicates a possible road corridor passing through the selected dataset extent.

The highlighted line represents a sample road layer and demonstrates how road-detection results can be visualized geographically.

This is built-in demonstration data and not a real road-detection result.
    `.trim();
  }

  if (
    normalizedQuery.includes("change") ||
    normalizedQuery.includes("between") ||
    normalizedQuery.includes("compare")
  ) {
    return `
The demonstration comparison indicates possible expansion of built-up areas inside the selected region.

Vegetation coverage may have reduced around the highlighted change area, while development appears to have increased between the selected time periods.

The orange polygon represents a sample change-detection layer. This is demonstration data and not a real temporal-analysis result.
    `.trim();
  }

  if (normalizedQuery.includes("sar")) {
    return `
The demonstration SAR interpretation highlights areas that may show different radar backscatter characteristics.

Bright regions can represent rough surfaces or built-up structures, while darker regions may represent smoother surfaces such as water.

This is a general demonstration and not a real SAR-processing result.
    `.trim();
  }

  if (normalizedQuery.includes("optical")) {
    return `
The demonstration optical-imagery result represents visible land-cover characteristics such as vegetation, water and built-up regions.

The interactive layers show how future optical-analysis outputs can be connected with their geographic locations.

This is built-in demonstration data and not a real optical-image analysis.
    `.trim();
  }

  if (
    normalizedQuery.includes("object") ||
    normalizedQuery.includes("present") ||
    normalizedQuery.includes("detect")
  ) {
    return `
The demonstration visualization contains sample building points, a road corridor, a possible flood region and a change-detection region.

Use the layer controls to show or hide each result type and inspect its geographic position.

These objects are generated for frontend demonstration and were not detected from the uploaded image.
    `.trim();
  }

  if (hasFile) {
    return `
The satellite image was accepted in Demo Mode.

The map shows a sample geographic extent along with built-in visualization layers for buildings, roads, flood regions and change areas.

This is demonstration data. Real results will replace it when the SatQuery backend and analysis services are connected.
    `.trim();
  }

  return `
SatQuery is currently running in Demo Mode.

The interactive map displays a sample Chennai dataset extent with built-in layers for buildings, roads, flood regions and change areas.

Connect the backend analysis API to replace this demonstration with real satellite observations.
  `.trim();
};

export const runMockAnalysis = async (
  query: string,
  file?: File | null
): Promise<QueryResponse> => {
  await wait(900);

  return {
    success: true,

    answer: generateRelatedAnswer(
      query,
      Boolean(file)
    ),

    dataset: createDemoDataset(file),

    confidence: null,
  };
};