import { useState } from "react";

import Navbar from "../components/layout/Navbar";
import QueryInput from "../components/query/QueryInput";
import QueryStatus from "../components/query/QueryStatus";
import ResultPanel from "../components/results/ResultPanel";

const Home = () => {
  const [query, setQuery] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  const handleAnalyze = (
    userQuery: string,
    file: File | null
  ) => {
    setQuery(userQuery);
    setSelectedFile(file);

    setAnalyzing(true);

    // Temporary frontend simulation
    setTimeout(() => {
      setAnalyzing(false);
    }, 2000);
  };

  return (
    <div className="app">

      <Navbar />

      <main className="main-container">

        <section className="hero">
          <h1>Query-Driven Earth Observation</h1>

          <p>
            Ask questions about satellite imagery using
            natural language.
          </p>
        </section>

        <div className="workspace">

          <div className="left-panel">

            <QueryInput
              onAnalyze={handleAnalyze}
            />

            <QueryStatus
              analyzing={analyzing}
            />

            <div className="map-container">

              <div className="map-placeholder">
                <span>🗺️</span>

                <h2>Satellite Map</h2>

                <p>
                  Satellite imagery and evidence
                  will appear here.
                </p>

                {selectedFile && (
                  <small>
                    Uploaded: {selectedFile.name}
                  </small>
                )}

              </div>

            </div>

          </div>

          <div className="right-panel">

            <ResultPanel
              query={query}
            />

          </div>

        </div>

      </main>

    </div>
  );
};

export default Home;