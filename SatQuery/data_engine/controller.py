"""Main controller for the SatQuery Data Engine."""

from pathlib import Path
from typing import Any

from data_engine.ingestion.file_validator import validate_file
from data_engine.ingestion.metadata_extractor import extract_metadata


SAR_POLARIZATIONS = {"VV", "VH", "HH", "HV"}


def _extract_sar_polarization(name: str) -> str | None:
    """
    Extract a recognized SAR polarization from a band name.

    Examples:
        VV      -> VV
        VH      -> VH
        "S1_VV" -> VV
        "SAR-VH" -> VH

    Returns None when no recognized SAR polarization is found.
    """
    tokens = (
        str(name)
        .upper()
        .replace("-", "_")
        .replace("/", "_")
        .split("_")
    )

    for token in tokens:
        if token in SAR_POLARIZATIONS:
            return token

    return None


def _detect_modality(
    metadata: dict[str, Any],
) -> tuple[str | None, list[str]]:
    """
    Detect raster modality from available band metadata.

    SAR is identified only when at least one recognized SAR
    polarization is present.

    Returns:
        A tuple containing:
        - modality: "sar" or None
        - detected SAR polarizations
    """
    polarizations = []

    for band in metadata.get("bands", []):
        polarization = _extract_sar_polarization(
            band.get("name", "")
        )

        if polarization and polarization not in polarizations:
            polarizations.append(polarization)

    if polarizations:
        return "sar", polarizations

    return None, []


def _validate_bands(
    metadata: dict[str, Any],
    modality: str | None,
    polarizations: list[str],
) -> dict[str, Any]:
    """
    Validate raster band consistency.

    General validation:
    - At least one band must exist.
    - All bands must have the same dimensions.
    - All bands must have the same data type.

    SAR-specific validation:
    - SAR evidence must exist.
    - Every SAR band must have recognized polarization metadata.
    """

    bands = metadata.get("bands", [])

    if not bands:
        return {
            "valid": False,
            "band_count": 0,
            "same_dtype": False,
            "same_dimensions": False,
            "dtypes": [],
            "dimensions": None,
            "reason": "No raster bands were found.",
        }

    dtypes = {
        str(band.get("dtype"))
        for band in bands
    }

    widths = {
        band.get("width")
        for band in bands
    }

    heights = {
        band.get("height")
        for band in bands
    }

    same_dtype = len(dtypes) == 1
    same_dimensions = (
        len(widths) == 1
        and len(heights) == 1
    )

    structurally_consistent = (
        same_dtype
        and same_dimensions
    )

    result = {
        "valid": structurally_consistent,
        "band_count": len(bands),
        "same_dtype": same_dtype,
        "same_dimensions": same_dimensions,
        "dtypes": sorted(dtypes),
        "dimensions": {
            "width": metadata["width"],
            "height": metadata["height"],
        },
    }

    # General band validation errors.
    if not same_dtype:
        result["reason"] = (
            "Raster bands have different data types."
        )

    elif not same_dimensions:
        result["reason"] = (
            "Raster bands have different dimensions."
        )

    # SAR-specific validation.
    if modality == "sar":
        band_polarizations = []

        for band in bands:
            polarization = _extract_sar_polarization(
                band.get("name", "")
            )
            band_polarizations.append(polarization)

        polarization_metadata_complete = all(
            polarization is not None
            for polarization in band_polarizations
        )

        # Ensure there are no duplicate polarization labels.
        unique_polarizations = [
            polarization
            for polarization in band_polarizations
            if polarization is not None
        ]

        duplicate_polarizations = (
            len(unique_polarizations)
            != len(set(unique_polarizations))
        )

        sar_valid = (
            structurally_consistent
            and polarization_metadata_complete
            and not duplicate_polarizations
        )

        result["sar_validation"] = {
            "is_sar": True,
            "polarizations": unique_polarizations,
            "polarization_metadata_complete": (
                polarization_metadata_complete
            ),
            "duplicate_polarizations": (
                duplicate_polarizations
            ),
            "structurally_consistent": (
                structurally_consistent
            ),
            "valid": sar_valid,
        }

        result["valid"] = sar_valid

        if not polarization_metadata_complete:
            result["reason"] = (
                "SAR raster has incomplete "
                "polarization metadata."
            )

        elif duplicate_polarizations:
            result["reason"] = (
                "SAR raster contains duplicate "
                "polarization labels."
            )

    return result


def process_file(path: str | Path) -> dict[str, Any]:
    """
    Validate and inspect a supported satellite image.

    This is the main entry point for the Rubin Data Engine.

    The controller:
    - validates the input file
    - extracts raster metadata
    - identifies SAR metadata when available
    - validates band consistency
    - extracts spatial information
    - returns a standardized Data Engine result

    It does not perform ML inference or semantic interpretation.
    """

    # 1. Basic file validation.
    file_info = validate_file(path)

    # 2. Raster/image metadata extraction.
    metadata = extract_metadata(path)

    # 3. Detect modality from available metadata.
    modality, polarizations = _detect_modality(
        metadata
    )

    # 4. Validate raster bands.
    band_validation = _validate_bands(
        metadata,
        modality,
        polarizations,
    )

    # 5. Build standardized raster information.
    geographic = metadata["geographic"]

    raster = {
        "width": metadata["width"],
        "height": metadata["height"],
        "bands": metadata["band_count"],
        "band_details": metadata.get("bands", []),
        "resolution": metadata["resolution"],
        "crs": (
            geographic["source_crs"]
            if geographic["source_crs"] is not None
            else None
        ),
        "modality": modality,
    }

    # 6. Build standardized spatial information.
    spatial = {
        "bounds": geographic["wgs84_bounds"],
        "centroid": geographic["centroid_wgs84"],
        "map_ready": geographic["map_ready"],
    }

    # 7. Return Data Engine result.
    return {
        "valid": (
            file_info["valid"]
            and band_validation["valid"]
        ),
        "raster": raster,
        "band_validation": band_validation,
        "spatial": spatial,
        "acquisition": {
            # Do not invent acquisition metadata.
            "datetime": None,
        },
    }