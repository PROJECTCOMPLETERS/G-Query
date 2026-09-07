interface ResultPanelProps {
  query: string;
}

const ResultPanel = ({ query }: ResultPanelProps) => {
  if (!query) {
    return (
      <div className="result-panel empty">
        <h2>Analysis Result</h2>
        <p>Enter a query to start satellite analysis.</p>
      </div>
    );
  }

  return (
    <div className="result-panel">
      <h2>🧠 Analysis Result</h2>

      <div className="query-display">
        <strong>Query:</strong>
        <p>{query}</p>
      </div>

      <div className="status">
        <span>●</span> Query received
      </div>

      <div className="evidence">
        <h3>Evidence</h3>

        <div className="evidence-item">
          ✓ Visual analysis
        </div>

        <div className="evidence-item">
          ✓ Temporal analysis
        </div>

        <div className="evidence-item">
          ✓ SAR analysis
        </div>

        <div className="evidence-item">
          ✓ Optical analysis
        </div>
      </div>

      <div className="confidence">
        <span>Confidence</span>
        <strong>--</strong>
      </div>
    </div>
  );
};

export default ResultPanel;