const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000";

export class ApiRequestError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
  }
}

export const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  try {
    const response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      options
    );

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const message =
        data?.detail ||
        data?.message ||
        getErrorMessage(response.status);

      throw new ApiRequestError(
        message,
        response.status
      );
    }

    return data as T;
  } catch (error) {
    if (error instanceof ApiRequestError) {
      throw error;
    }

    throw new ApiRequestError(
      "SatQuery server is unavailable. Please try again.",
      0
    );
  }
};

const getErrorMessage = (status: number) => {
  switch (status) {
    case 400:
      return "The request is invalid. Please check your input.";

    case 404:
      return "The requested dataset was not found.";

    case 413:
      return "The selected file is too large.";

    case 415:
      return "Only JPG, PNG and GeoTIFF files are supported.";

    case 422:
      return "The server could not validate this satellite file.";

    case 500:
      return "The server could not process this satellite image.";

    default:
      return "Something went wrong. Please try again.";
  }
};