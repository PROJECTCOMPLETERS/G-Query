import type { QueryResponse } from "../../types/query";
import {
  queryCapabilities,
  safeError,
} from "../../api/queryApi";

interface Props {
  response?: QueryResponse;
  busy?: boolean;
  stopped?: boolean;
  latest?: boolean;

  onRetry: () => void;
  onData: () => void;
  onAnswer: (answer: string) => void;
}

export default function QueryStatus({
  response,
  busy,
  stopped,
  latest,
  onRetry,
  onData,
  onAnswer,
}: Props) {
  if (stopped) {
    return <p className="phase-status">Response stopped.</p>;
  }

  if (!response) {
    return (
      <p className="phase-status" role="status">
        {busy
          ? "Sending your request…"
          : "No response received."}
      </p>
    );
  }

  const labels: Record<QueryResponse["status"], string> = {
    READY: "Understanding confirmed",
    NEEDS_CLARIFICATION: "Clarification needed",
    WAITING_FOR_DATA: "Checking your data",
    NOT_READY: "Data is not ready",
    EXECUTING: "Running analysis",
    COMPLETED: "Analysis complete",
    FAILED: "Analysis failed",
    UNSUPPORTED: "Outside supported capabilities",

    RECEIVED: "Request received",
    VALIDATING: "Understanding your query",
    TASK_IDENTIFIED: "Task identified",
    REQUIREMENTS_CHECKED: "Requirements checked",
    EXECUTION_PLANNED: "Execution planned",
  };

  return (
    <section
      className={`phase-status ${response.status.toLowerCase()}`}
      aria-label={response.status}
    >
      <strong
        role={response.status === "FAILED" ? "alert" : "status"}
      >
        {labels[response.status]}
        {busy ? "…" : ""}
      </strong>

      {response.status === "NEEDS_CLARIFICATION" && (
        <>
          <p>
            {response.question ||
              "The backend has not returned a clarification question yet."}
          </p>

          {response.question &&
            response.options?.map((answer) => (
              <button
                key={answer}
                disabled={
                  !latest ||
                  busy ||
                  !queryCapabilities.clarify
                }
                onClick={() => onAnswer(answer)}
              >
                {answer}
              </button>
            ))}

          {!queryCapabilities.clarify && (
            <small>
              Clarification replies will be available when
              the backend endpoint is connected.
            </small>
          )}
        </>
      )}

      {response.status === "NOT_READY" && (
        <>
          <p>
            {response.reason ||
              "Select suitable observations for this task."}
          </p>

          <button
            disabled={busy || !latest}
            onClick={onData}
          >
            Select another dataset
          </button>
        </>
      )}

      {response.status === "UNSUPPORTED" && (
        <p>
          {response.reason ||
            "This type of analysis is not supported."}
        </p>
      )}

      {response.status === "FAILED" && (
        <>
          <p>{safeError(response)}</p>

          {response.error?.recoverable === true && (
            <>
              <button
                disabled={
                  busy ||
                  !latest ||
                  !queryCapabilities.retry
                }
                onClick={onRetry}
              >
                Retry
              </button>

              {!queryCapabilities.retry && (
                <small>
                  The backend Retry endpoint is not connected yet.
                </small>
              )}
            </>
          )}
        </>
      )}
    </section>
  );
}