interface QueryStatusProps {
  analyzing: boolean;
}

const QueryStatus = ({ analyzing }: QueryStatusProps) => {
  if (!analyzing) return null;

  return (
    <div className="query-status" role="status" aria-live="polite">
      <div className="assistant-status-avatar">🛰️</div>

      <div className="generating-status">
        <strong>SatQuery AI</strong>

        <div className="typing-indicator" aria-label="Generating response">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  );
};

export default QueryStatus;