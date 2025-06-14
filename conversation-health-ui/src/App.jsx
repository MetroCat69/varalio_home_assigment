import React, { useEffect, useState } from "react";
import { AlertCircle, Wifi, WifiOff } from "lucide-react";
import InputPanel from "./components/input/InputPanel";
import ResultsPanel from "./components/analysis/ResultsPanel";
import { useAnalysis } from "./hooks/useAnalysis";

function App() {
  const {
    isAnalyzing,
    results,
    error,
    analyzeConversation,
    saveResultsToJson,
    checkApiHealth,
  } = useAnalysis();

  const [apiStatus, setApiStatus] = useState("checking");

  // Check API health on component mount
  useEffect(() => {
    const checkStatus = async () => {
      const isHealthy = await checkApiHealth();
      setApiStatus(isHealthy ? "connected" : "disconnected");
    };

    checkStatus();

    // Check every 30 seconds
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, [checkApiHealth]);

  const handleAnalyze = async (transcript, testCase) => {
    try {
      await analyzeConversation(transcript, testCase);
    } catch (err) {
      console.error("Analysis failed:", err);
    }
  };

  const handleSaveResults = () => {
    try {
      saveResultsToJson("conversation-analysis");
    } catch (err) {
      console.error("Save failed:", err);
      // You could show a toast notification here
    }
  };

  const getApiStatusBadge = () => {
    switch (apiStatus) {
      case "connected":
        return (
          <div className="flex items-center gap-2 text-xs text-green-700 bg-green-50 px-2 py-1 rounded-full border border-green-200">
            <Wifi className="w-3 h-3" />
            API Connected
          </div>
        );
      case "disconnected":
        return (
          <div className="flex items-center gap-2 text-xs text-red-700 bg-red-50 px-2 py-1 rounded-full border border-red-200">
            <WifiOff className="w-3 h-3" />
            API Disconnected
          </div>
        );
      default:
        return (
          <div className="flex items-center gap-2 text-xs text-gray-700 bg-gray-50 px-2 py-1 rounded-full border border-gray-200">
            <div className="w-3 h-3 border border-gray-400 border-t-transparent rounded-full animate-spin" />
            Checking API
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg shadow-lg p-6 mb-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">
                Conversation Health Analysis
              </h1>
              <p className="text-indigo-100">
                Analyze conversation quality with detailed metrics and visual
                insights
              </p>
            </div>
            <div className="flex flex-col items-end gap-2">
              {getApiStatusBadge()}
              <div className="text-indigo-200 text-xs">FastAPI Backend</div>
            </div>
          </div>
        </div>

        {/* API Connection Error */}
        {apiStatus === "disconnected" && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-amber-600" />
              <h4 className="font-medium text-amber-800">
                API Connection Issue
              </h4>
            </div>
            <p className="text-amber-700 text-sm mt-1">
              Cannot connect to the FastAPI backend at localhost:8000. Please
              ensure your backend server is running.
            </p>
            <div className="mt-2 text-xs text-amber-600">
              Run:{" "}
              <code className="bg-amber-100 px-1 rounded">python main.py</code>{" "}
              to start the backend
            </div>
          </div>
        )}

        {/* Analysis Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <h4 className="font-medium text-red-800">Analysis Error</h4>
            </div>
            <p className="text-red-700 text-sm mt-1">{error}</p>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel - Input */}
          <div className="lg:col-span-1">
            <InputPanel
              onAnalyze={handleAnalyze}
              onSaveResults={handleSaveResults}
              isAnalyzing={isAnalyzing}
              hasResults={!!results}
            />
          </div>

          {/* Right Panel - Results */}
          <div className="lg:col-span-2">
            <ResultsPanel results={results} isLoading={isAnalyzing} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
