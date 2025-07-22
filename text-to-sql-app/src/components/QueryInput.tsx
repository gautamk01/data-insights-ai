"use client";

interface QueryInputProps {
  question: string;
  setQuestion: (value: string) => void;
  isLoading: boolean;
  handleAskQuestion: () => void;
  handleClearResults: () => void;
}

const QueryInput = ({
  question,
  setQuestion,
  isLoading,
  handleAskQuestion,
  handleClearResults,
}: QueryInputProps) => {
  const quickQuestions = [
    "What are my top 5 products by sales?",
    "Show me daily revenue trends",
    "What is my total sales ",
    "Calculate the RoAS (Return on Ad Spend)",
    "Which product had the highest CPC (Cost Per Click)?",
    "Give me a breakdown of ad spend by product for all items",
  ];

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleAskQuestion();
    }
  };

  return (
    <>
      <div className="input-section">
        <label htmlFor="question">Ask a question about your data:</label>
        <input
          type="text"
          id="question"
          placeholder="e.g., What are my top 5 products by sales?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
        />
      </div>

      <div className="quick-questions">
        <h3>Quick Test Questions:</h3>
        {quickQuestions.map((q) => (
          <button
            key={q}
            className="question-btn"
            onClick={() => setQuestion(q)}
            disabled={isLoading}
          >
            {q}
          </button>
        ))}
      </div>

      <div>
        <button onClick={handleAskQuestion} disabled={isLoading}>
          {isLoading ? "Generating..." : "🚀 Generate Visualization"}
        </button>
        <button onClick={handleClearResults} disabled={isLoading}>
          🧹 Clear Results
        </button>
      </div>
    </>
  );
};

export default QueryInput;
