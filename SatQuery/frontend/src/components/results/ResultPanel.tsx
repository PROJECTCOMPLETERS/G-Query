import DatasetInfo from "./DatasetInfo";
import MapView from "../map/MapView";

import type { Dataset } from "../../types/dataset";

export interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  fileName?: string;
  imageUrl?: string;
  dataset?: Dataset;
  error?: boolean;
  demoMode?: boolean;
}

interface ResultPanelProps {
  messages: ChatMessage[];
}

const ResultPanel = ({
  messages,
}: ResultPanelProps) => {
  const copyResponse = async (
    content: string
  ) => {
    try {
      await navigator.clipboard.writeText(content);
    } catch {
      console.error("Unable to copy response");
    }
  };

  return (
    <div className="conversation">
      {messages.map((message) => (
        <article
          key={message.id}
          className={`message ${message.role} ${
            message.error ? "error-message" : ""
          }`}
        >
          <div className="message-avatar">
            {message.role === "user" ? "P" : "🛰️"}
          </div>

          <div className="message-content">
            <strong>
              {message.role === "user"
                ? "You"
                : "SatQuery AI"}
            </strong>

            {message.demoMode && (
              <span className="response-demo-badge">
                Demo Mode
              </span>
            )}

            {message.imageUrl && (
              <img
                className="message-image"
                src={message.imageUrl}
                alt={
                  message.fileName ||
                  "Uploaded satellite image"
                }
              />
            )}

            {message.fileName &&
              !message.imageUrl && (
                <div className="message-file">
                  📎 {message.fileName}
                </div>
              )}

            {message.content && (
              <p>{message.content}</p>
            )}

            {message.dataset && (
              <>
                <DatasetInfo
                  dataset={message.dataset}
                />

                <MapView
                  spatial={message.dataset.spatial}
                  demoMode={message.demoMode}
                />
              </>
            )}

            {message.role === "assistant" &&
              !message.error && (
                <div className="message-actions">
                  <button
                    type="button"
                    className="message-action"
                    onClick={() =>
                      copyResponse(message.content)
                    }
                  >
                    Copy response
                  </button>
                </div>
              )}
          </div>
        </article>
      ))}
    </div>
  );
};

export default ResultPanel;