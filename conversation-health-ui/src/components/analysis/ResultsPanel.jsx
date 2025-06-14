import React from "react";
import { MessageSquare } from "lucide-react";
import OverallScore from "./OverallScore";
import OverallAssessment from "./OverallAssessment";
import CriteriaGrid from "./CriteriaGrid";
import QualityIndicators from "./QualityIndicators";
import UncertaintyInfo from "./UncertaintyInfo";

const ResultsPanel = ({ results, isLoading = false }) => {
  if (isLoading) {
    return <LoadingState />;
  }

  if (!results) {
    return <EmptyState />;
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <OverallScore results={results} />
      <OverallAssessment results={results} />
      <CriteriaGrid results={results} />
      <QualityIndicators results={results} />
      <UncertaintyInfo results={results} />
    </div>
  );
};

const LoadingState = () => (
  <div className="bg-white rounded-lg shadow-sm p-12 text-center">
    <div className="flex flex-col items-center gap-4">
      <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
      <div className="space-y-2">
        <h3 className="text-lg font-medium text-gray-900">
          Analyzing Conversation
        </h3>
        <p className="text-gray-600">
          Processing conversation health metrics and quality indicators...
        </p>
      </div>
    </div>
  </div>
);

const EmptyState = () => (
  <div className="bg-white rounded-lg shadow-sm p-12 text-center">
    <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
    <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Analyze</h3>
    <p className="text-gray-600 max-w-md mx-auto">
      Enter a conversation transcript or select a test case, then click
      "Analyze" to see detailed health metrics with points breakdown and
      explanations.
    </p>
  </div>
);

export default ResultsPanel;
