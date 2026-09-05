import { useState } from "react";
import FileUploader from "../upload/FileUploader";
import SuggestedQueries from "./SuggestedQueries";

interface QueryInputProps {
  onAnalyze: (query: string, file: File | null) => void;
}

const QueryInput = ({ onAnalyze }: QueryInputProps) => {
  const [query, setQuery] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const handleAnalyze = () => {
    if (!query.trim()) {
      alert("Please enter a query.");
      return;
    }

    onAnalyze(query, file);
  };

  return (
    <div className="query-section">

      <label>Ask SatQuery AI</label>

      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Example: How has this region changed between 2020 and 2025?"
        rows={4}
      />

      <SuggestedQueries onSelect={setQuery} />

      <div className="query-actions">

        <FileUploader onFileSelect={setFile} />

        <button
          className="analyze-btn"
          onClick={handleAnalyze}
        >
          🔍 Analyze
        </button>

      </div>

    </div>
  );
};

export default QueryInput;