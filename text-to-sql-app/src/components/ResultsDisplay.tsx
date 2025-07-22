interface VizResult {
  answer: string;
  sql: string;
  chart_type: string;
  chart_data: any;
}

interface ResultsDisplayProps {
  result: VizResult;
}

const ResultsDisplay = ({ result }: ResultsDisplayProps) => {
  return (
    <div className="result-section">
      <div className="result-item">
        <div className="result-label">Answer:</div>
        <div className="result-value">
          {result.answer || "No answer provided."}
        </div>
      </div>
      <div className="result-item">
        <div className="result-label">Generated SQL:</div>
        <div className="result-value">{result.sql || "No SQL generated."}</div>
      </div>
      <div className="result-item">
        <div className="result-label">Chart Type:</div>
        <div className="result-value">{result.chart_type || "none"}</div>
      </div>
      <div className="result-item">
        <div className="result-label">Raw Chart Data:</div>
        <div className="result-value">
          {JSON.stringify(result.chart_data, null, 2)}
        </div>
      </div>
    </div>
  );
};

export default ResultsDisplay;
