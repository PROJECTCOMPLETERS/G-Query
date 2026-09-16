import axios from "axios";
import api from "./client";

import {
  querySchema,
  type QueryInput,
  type QueryResponse,
} from "../types/query";

// Configure only after the backend exposes these endpoints.
const paths = {
  status: import.meta.env.VITE_QUERY_STATUS_PATH as string | undefined,
  clarify: import.meta.env.VITE_QUERY_CLARIFY_PATH as string | undefined,
  retry: import.meta.env.VITE_QUERY_RETRY_PATH as string | undefined,
};

export const queryCapabilities = {
  status: !!paths.status,
  clarify: !!paths.clarify,
  retry: !!paths.retry,
};

const route = (path: string, requestId: string) =>
  path.replace("{request_id}", encodeURIComponent(requestId));

export function parseQuery(data: unknown, expectedId?: string) {
  const result = querySchema.parse(data);

  if (expectedId && result.request_id !== expectedId) {
    throw new Error("Request identity mismatch");
  }

  return result;
}

export async function submitQuery(
  input: QueryInput,
  signal: AbortSignal
) {
  const { data } = await api.post("/api/v1/query", input, {
    signal,
    timeout: 30000,
  });

  // Current backend generates the ID.
  // Every subsequent operation uses that returned ID.
  return parseQuery(data);
}

export async function clarifyQuery(
  requestId: string,
  answer: string,
  inputs: QueryInput["inputs"],
  signal: AbortSignal
) {
  if (!paths.clarify) {
    throw new Error("Clarification endpoint is not configured");
  }

  const { data } = await api.post(
    route(paths.clarify, requestId),
    {
      request_id: requestId,
      answer,
      inputs,
    },
    {
      signal,
      timeout: 30000,
    }
  );

  return parseQuery(data, requestId);
}

export async function retryQuery(
  requestId: string,
  signal: AbortSignal
) {
  if (!paths.retry) {
    throw new Error("Retry endpoint is not configured");
  }

  const { data } = await api.post(
    route(paths.retry, requestId),
    { request_id: requestId },
    { signal, timeout: 30000 }
  );

  return parseQuery(data, requestId);
}

const terminalStates = new Set([
  "NEEDS_CLARIFICATION",
  "NOT_READY",
  "COMPLETED",
  "FAILED",
  "UNSUPPORTED",
]);

export async function followQuery(
  first: QueryResponse,
  update: (response: QueryResponse) => void,
  signal: AbortSignal
) {
  let current = first;
  update(current);

  if (!terminalStates.has(current.status) && !paths.status) {
    return "Request accepted. Live status updates are not connected yet.";
  }

  for (let attempt = 0; !terminalStates.has(current.status); attempt++) {
    if (attempt >= 60) {
      return "Updates paused after 60 checks. The backend may still be processing this request.";
    }

    await new Promise<void>((resolve, reject) => {
      if (signal.aborted) {
        reject(new DOMException("Aborted", "AbortError"));
        return;
      }

      const abort = () => {
        clearTimeout(timer);
        reject(new DOMException("Aborted", "AbortError"));
      };

      const timer = setTimeout(() => {
        signal.removeEventListener("abort", abort);
        resolve();
      }, 1200);

      signal.addEventListener("abort", abort, { once: true });
    });

    const { data } = await api.get(
      route(paths.status!, first.request_id),
      {
        signal,
        timeout: 10000,
      }
    );

    current = parseQuery(data, first.request_id);
    update(current);
  }
}

export function queryFailure(
  error: unknown,
  requestId: string
): QueryResponse {
  if (axios.isAxiosError(error)) {
    const parsed = querySchema.safeParse(error.response?.data);

    if (
      parsed.success &&
      parsed.data.request_id === requestId
    ) {
      return parsed.data;
    }
  }

  const code = axios.isAxiosError(error)
    ? error.response
      ? "REQUEST_REJECTED"
      : "CONNECTION_ERROR"
    : "INVALID_RESPONSE";

  return {
    request_id: requestId,
    status: "FAILED",
    error: {
      code,
      message: "Request could not be completed",
      stage: "frontend",
      recoverable: false,
    },
  };
}

export function safeError(response: QueryResponse) {
  const messages: Record<string, string> = {
    DATA_INSUFFICIENT:
      "This image does not have enough detail. Select a higher-resolution observation.",

    DATASET_NOT_FOUND:
      "This dataset is unavailable. Select another dataset.",

    CONNECTION_ERROR:
      "Could not reach the backend. Check the connection before submitting again.",

    INVALID_RESPONSE:
      "The backend returned an incomplete or incompatible response.",

    REQUEST_REJECTED:
      "The backend could not accept this request. Check your data and try again.",
  };

  return (
    messages[response.error?.code || ""] ||
    "The analysis could not finish. Check your inputs or contact the project team."
  );
}