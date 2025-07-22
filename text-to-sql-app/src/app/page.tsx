"use client";

import { useState } from "react";
import QueryInput from "@/components/QueryInput";
import ResultsDisplay from "@/components/ResultsDisplay";
import DataChart from "@/components/DataChart";
import ProgressBar from "@/components/progress";

// ... (keep the VizResult interface)
interface VizResult {
  answer: string;
  sql: string;
  chart_type: string;
  chart_data: any;
  success: boolean;
  debug_info?: any;
}

export default function Home() {
  const [question, setQuestion] = useState<string>("");
  const [result, setResult] = useState<VizResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // ... (keep your API_BASE, handleAskQuestion, and handleClearResults functions)
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE;

  const handleAskQuestion = async () => {
    if (!question.trim()) {
      setError("Please enter a question");
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE}/ask/viz`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data: VizResult = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(
          data.answer || "An unknown error occurred on the server."
        );
      }

      setResult(data);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearResults = () => {
    setQuestion("");
    setResult(null);
    setError(null);
    setIsLoading(false);
  };

  return (
    <div className="container">
      <h1>📊 Text-to-SQL Visualization System</h1>

      <QueryInput
        question={question}
        setQuestion={setQuestion}
        isLoading={isLoading}
        handleAskQuestion={handleAskQuestion}
        handleClearResults={handleClearResults}
      />

      {/* Conditionally render the progress bar */}
      {isLoading && <ProgressBar />}

      {error && <div className="error result-section">{error}</div>}

      {result && result.success && (
        <>
          <ResultsDisplay result={result} />
          {result.chart_data && result.chart_type !== "none" && (
            <DataChart type={result.chart_type} data={result.chart_data} />
          )}
        </>
      )}
    </div>
  );
}
