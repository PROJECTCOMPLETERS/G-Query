import { useState } from "react";
import FileUploader from "../upload/FileUploader";

interface QueryInputProps {
  onAnalyze: (query: string, file: File | null) => void;
  analyzing: boolean;
}

const QueryInput = ({
  onAnalyze,
  analyzing,
}: QueryInputProps) => {
  const [query, setQuery] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");

  const handleAnalyze = () => {
    const cleanedQuery = query.trim();

    if (!cleanedQuery && !file) {
      setError(
        "Enter a query or attach a satellite image."
      );
      return;
    }

    setError("");
    onAnalyze(cleanedQuery, file);

    setQuery("");
    setFile(null);
  };

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey &&
      !analyzing
    ) {
      event.preventDefault();
      handleAnalyze();
    }
  };

  return (
    <div className="composer-wrapper">
      <div className="composer">
        {file && (
          <FileUploader
            file={file}
            onFileSelect={setFile}
          />
        )}

        <textarea
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setError("");
          }}
          onKeyDown={handleKeyDown}
          placeholder="Ask SatQuery about satellite imagery..."
          rows={1}
          disabled={analyzing}
          aria-label="Enter a satellite imagery query"
        />

        <div className="composer-actions">
          {!file && (
            <FileUploader
              file={file}
              onFileSelect={setFile}
            />
          )}

          <span className="input-hint">
            JPG, PNG or GeoTIFF
          </span>

          <button
            type="button"
            className="send-btn"
            onClick={handleAnalyze}
            disabled={
              analyzing || (!query.trim() && !file)
            }
            aria-label="Send query"
          >
            {analyzing ? "•••" : "➤"}
          </button>
        </div>
      </div>

      {error && (
        <p className="composer-error" role="alert">
          {error}
        </p>
      )}

      <p className="composer-note">
        SatQuery can make mistakes. Verify important
        satellite observations.
      </p>
    </div>
  );
};

export default QueryInput;