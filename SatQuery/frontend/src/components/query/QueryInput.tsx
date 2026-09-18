import {
  useEffect,
  useRef,
  useState,
} from "react";

import FileUploader from "../upload/FileUploader";

interface QueryInputProps {
  query: string;

  onQuery: (value: string) => void;

  onAnalyze: (
    query: string,
    file: File | null
  ) => Promise<void>;

  analyzing: boolean;

  onStop: () => void;

  clarification: boolean;

  blocked: boolean;
}

const QueryInput = ({
  query,
  onQuery,
  onAnalyze,
  analyzing,
  onStop,
  clarification,
  blocked,
}: QueryInputProps) => {
  const [file, setFile] =
    useState<File | null>(null);

  const textareaRef =
    useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const textarea = textareaRef.current;

    if (!textarea) return;

    textarea.style.height = "auto";

    textarea.style.height = `${
      Math.min(textarea.scrollHeight, 160)
    }px`;
  }, [query]);

  const handleSend = () => {
    if (
      analyzing ||
      blocked ||
      (!query.trim() && !file)
    ) {
      return;
    }

    const cleanedQuery = query.trim();
    const selectedFile = file;

    onQuery("");
    setFile(null);

    void onAnalyze(cleanedQuery, selectedFile);
  };

  return (
    <div className="composer-wrapper">
      {clarification && (
        <p className="clarification-hint">
          {blocked
            ? "Clarification is waiting for the backend reply endpoint."
            : "Your reply continues the same request."}
        </p>
      )}

      <div className="composer">
        <textarea
          ref={textareaRef}
          value={query}
          onChange={(event) => {
            onQuery(event.target.value);
          }}
          onKeyDown={(event) => {
            if (
              event.key === "Enter" &&
              !event.shiftKey &&
              !event.nativeEvent.isComposing
            ) {
              event.preventDefault();
              handleSend();
            }
          }}
          placeholder={
            clarification
              ? "Answer the clarification…"
              : "Ask SatQuery about satellite imagery…"
          }
          rows={1}
          disabled={blocked}
          aria-label="Message SatQuery"
        />

        <div className="composer-actions">
          <fieldset
            className="upload-controls"
            disabled={analyzing || blocked}
          >
            <FileUploader
              file={file}
              onFileSelect={setFile}
            />
          </fieldset>

          <span className="input-hint">
            Enter to send · Shift + Enter for newline
          </span>

          {analyzing ? (
            <button
              type="button"
              className="send-btn"
              onClick={onStop}
              aria-label="Stop response"
            >
              ■
            </button>
          ) : (
            <button
              type="button"
              className="send-btn"
              onClick={handleSend}
              disabled={
                blocked ||
                (!query.trim() && !file)
              }
              aria-label="Send query"
            >
              ➤
            </button>
          )}
        </div>
      </div>

      <p className="composer-note">
        Check results against the source observations.
      </p>
    </div>
  );
};

export default QueryInput;