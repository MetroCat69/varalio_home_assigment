import { useState, useCallback } from "react";
import { TEST_CASES, API_CONFIG } from "../utils/constants";

export const useAnalysis = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const analyzeConversation = useCallback(
    async (transcript, selectedTestCase) => {
      setIsAnalyzing(true);
      setError(null);

      try {
        // Get the actual transcript content
        let actualTranscript = transcript;
        if (
          selectedTestCase &&
          selectedTestCase !== "custom" &&
          TEST_CASES[selectedTestCase]
        ) {
          actualTranscript = TEST_CASES[selectedTestCase].transcript;
        }

        if (!actualTranscript.trim()) {
          throw new Error("Transcript cannot be empty");
        }

        // Call your FastAPI backend with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(
          () => controller.abort(),
          API_CONFIG.TIMEOUT
        );

        const response = await fetch(`${API_CONFIG.BASE_URL}/analyze`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            transcript: actualTranscript,
            test_case: selectedTestCase,
          }),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(
            errorData.detail || `HTTP error! status: ${response.status}`
          );
        }

        const analysisResults = await response.json();
        setResults(analysisResults);
        return analysisResults;
      } catch (err) {
        if (err.name === "AbortError") {
          setError("Analysis timed out. Please try again.");
        } else if (err.message.includes("fetch")) {
          setError(
            "Cannot connect to analysis server. Please ensure the backend is running."
          );
        } else {
          setError(err.message || "Analysis failed");
        }
        throw err;
      } finally {
        setIsAnalyzing(false);
      }
    },
    []
  );

  const saveResultsToJson = useCallback(
    (filename = "conversation-analysis") => {
      if (!results) {
        throw new Error("No analysis results to save");
      }

      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      const exportData = {
        metadata: {
          exportedAt: new Date().toISOString(),
          filename: `${filename}_${timestamp}.json`,
          version: "1.0.0",
          source: "FastAPI Backend Analysis",
        },
        analysisResults: results,
      };

      const dataStr = JSON.stringify(exportData, null, 2);
      const dataBlob = new Blob([dataStr], { type: "application/json" });

      const link = document.createElement("a");
      link.href = URL.createObjectURL(dataBlob);
      link.download = `${filename}_${timestamp}.json`;
      link.click();

      // Clean up
      URL.revokeObjectURL(link.href);
    },
    [results]
  );

  const clearResults = useCallback(() => {
    setResults(null);
    setError(null);
  }, []);

  const checkApiHealth = useCallback(async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout for health check

      const response = await fetch(`${API_CONFIG.BASE_URL}/health`, {
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      return response.ok;
    } catch (err) {
      console.error("API health check failed:", err);
      return false;
    }
  }, []);

  return {
    isAnalyzing,
    results,
    error,
    analyzeConversation,
    saveResultsToJson,
    clearResults,
    checkApiHealth,
  };
};
