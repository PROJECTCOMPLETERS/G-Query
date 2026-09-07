interface SuggestedQueriesProps {
  onSelect: (query: string) => void;
}

const SuggestedQueries = ({
  onSelect,
}: SuggestedQueriesProps) => {
  const queries = [
    "What objects are present in this image?",
    "How has this region changed between 2020 and 2025?",
    "What does the SAR imagery indicate?",
    "Compare SAR and Optical imagery.",
  ];

  return (
    <div className="suggested">
      <h3>Suggested Queries</h3>

      <div className="suggested-list">
        {queries.map((query) => (
          <button
            key={query}
            onClick={() => onSelect(query)}
          >
            {query}
          </button>
        ))}
      </div>
    </div>
  );
};

export default SuggestedQueries;