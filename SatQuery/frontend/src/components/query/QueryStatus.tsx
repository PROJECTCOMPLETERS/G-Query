interface QueryStatusProps {
  analyzing: boolean;
}

const QueryStatus = ({ analyzing }: QueryStatusProps) => {
  if (!analyzing) return null;

  return (
    <div className="analysis-status">
      <div className="spinner"></div>

      <div>
        <strong>Analyzing satellite data...</strong>
        <p>
          SatQuery is selecting the required analysis pathway.
        </p>
      </div>
    </div>
  );
};

export default QueryStatus;