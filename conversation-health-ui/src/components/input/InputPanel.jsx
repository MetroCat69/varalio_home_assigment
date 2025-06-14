import React, { useState } from "react";
import { Play, Save, Download, Settings } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import Button from "../ui/Button";
import TestCaseSelector from "./TestCaseSelector";
import ConversationInput from "./ConversationInput";

const InputPanel = ({
  onAnalyze,
  onSaveResults,
  isAnalyzing = false,
  hasResults = false,
}) => {
  const [activeTab, setActiveTab] = useState("test");
  const [selectedTest, setSelectedTest] = useState("positive_resolution");
  const [customTranscript, setCustomTranscript] = useState("");

  const handleAnalyze = () => {
    const transcript = activeTab === "custom" ? customTranscript : "";
    const testCase = activeTab === "test" ? selectedTest : "custom";
    onAnalyze(transcript, testCase);
  };

  const handleSave = () => {
    if (hasResults && onSaveResults) {
      onSaveResults();
    }
  };

  const handleCustomTranscriptChange = (e) => {
    setCustomTranscript(e.target.value);
  };

  const canAnalyze = () => {
    if (activeTab === "custom") {
      return customTranscript.trim().length > 0;
    }
    return selectedTest && selectedTest !== "custom";
  };

  return (
    <Card className="h-fit">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-gray-400" />
            Input
          </CardTitle>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Tab Selection */}
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab("test")}
            className={`px-4 py-2 font-medium text-sm transition-colors ${
              activeTab === "test"
                ? "border-b-2 border-indigo-500 text-indigo-600"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Test Cases
          </button>
          <button
            onClick={() => setActiveTab("custom")}
            className={`px-4 py-2 font-medium text-sm transition-colors ${
              activeTab === "custom"
                ? "border-b-2 border-indigo-500 text-indigo-600"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            Custom Input
          </button>
        </div>

        {/* Test Case Selection */}
        {activeTab === "test" && (
          <TestCaseSelector
            selectedTest={selectedTest}
            onTestChange={setSelectedTest}
          />
        )}

        {/* Conversation Input */}
        <ConversationInput
          value={customTranscript}
          onChange={handleCustomTranscriptChange}
          selectedTest={activeTab === "test" ? selectedTest : "custom"}
          disabled={isAnalyzing}
        />

        {/* Action Buttons */}
        <div className="flex gap-3 pt-2">
          <Button
            onClick={handleAnalyze}
            disabled={!canAnalyze() || isAnalyzing}
            className="flex-1"
          >
            {isAnalyzing ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Analyze
              </>
            )}
          </Button>

          <Button
            variant="outline"
            size="default"
            disabled={!hasResults || isAnalyzing}
            onClick={handleSave}
            title={
              hasResults
                ? "Save analysis results to JSON file"
                : "Run analysis first to save results"
            }
          >
            <Download className="w-4 h-4" />
          </Button>
        </div>

        {/* API Status Indicator */}
        <div className="flex items-center gap-2 text-xs text-gray-500 pt-2 border-t">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span>Connected to FastAPI backend</span>
        </div>
      </CardContent>
    </Card>
  );
};

export default InputPanel;
