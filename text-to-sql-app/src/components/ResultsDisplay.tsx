import React from "react";

interface VizResult {
  answer: string;
  sql: string;
  chart_type: string;
  chart_data: any;
  success: boolean;
  debug_info?: any;
}

interface ResultsDisplayProps {
  result: VizResult;
}

// Define formatters once for efficiency
const currencyFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 2,
});

const numberFormatter = new Intl.NumberFormat("en-IN");

const formatCell = (header: string, value: any): string => {
  if (value === null || value === undefined) {
    return "N/A";
  }
  const currencyColumns = [
    "ad_spend",
    "ad_sales",
    "total_sales",
    "spend",
    "revenue",
  ];
  if (currencyColumns.includes(header.toLowerCase())) {
    return currencyFormatter.format(Number(value));
  }
  const floatColumns = ["cpc", "roas"];
  if (floatColumns.includes(header.toLowerCase())) {
    return Number(value).toFixed(2);
  }
  if (header.toLowerCase() === "date") {
    return String(value).substring(0, 10);
  }
  if (typeof value === "number") {
    return numberFormatter.format(value);
  }
  return String(value);
};

const ResultsDisplay = ({ result }: ResultsDisplayProps) => {
  const renderAnswer = (answer: string) => {
    try {
      if (!answer.includes("[{") && !answer.includes("}]")) {
        return answer;
      }
      const startIndex = answer.indexOf("[");
      const endIndex = answer.lastIndexOf("]");
      const jsonString = answer.substring(startIndex, endIndex + 1);

      let parsableString = jsonString.replace(/\bNone\b/g, "null");

      let validJsonString = "";
      let inDoubleQuotes = false;
      for (const char of parsableString) {
        if (char === '"') {
          inDoubleQuotes = !inDoubleQuotes;
        }
        if (char === "'" && !inDoubleQuotes) {
          validJsonString += '"';
        } else {
          validJsonString += char;
        }
      }

      const data = JSON.parse(validJsonString);

      if (Array.isArray(data) && data.length > 0) {
        const headers = Object.keys(data[0]);
        return (
          <table className="result-table">
            <thead>
              <tr>
                {headers.map((header) => (
                  <th key={header}>{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, index) => (
                // --- FIX: Create a unique composite key ---
                <tr key={`${row.item_id}-${index}`}>
                  {headers.map((header) => (
                    <td key={header}>{formatCell(header, row[header])}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        );
      }
    } catch (error) {
      console.error("Failed to parse answer data:", error);
      console.error("Invalid JSON string:", result.answer);
      return answer;
    }
    return answer;
  };

  return (
    <div className="result-section">
      <div className="result-item">
        <div className="result-label">Answer:</div>
        <div className="result-value">{renderAnswer(result.answer)}</div>
      </div>
      <div className="result-item">
        <div className="result-label">Generated SQL:</div>
        <div className="result-value">{result.sql || "No SQL generated."}</div>
      </div>
    </div>
  );
};

export default ResultsDisplay;
