import React, { useState } from "react";
import {
  AlertCircle,
  CheckCircle,
  XCircle,
  TrendingUp,
  TrendingDown,
  MessageSquare,
  Settings,
  Play,
  Save,
  Upload,
} from "lucide-react";

const ConversationHealthMockup = () => {
  const [activeTab, setActiveTab] = useState("test");
  const [selectedTest, setSelectedTest] = useState("custom");
  const [showResults, setShowResults] = useState(false);

  const mockResults = {
    finalScore: 72,
    healthLevel: "good",
    overallAssessment:
      "Overall, the conversation earned a solid 72/100 \"Good\" health score with high confidence, demonstrating strong empathy and professionalism throughout the interaction. The agent effectively acknowledged the customer's frustration and provided a clear resolution path, earning high marks for sentiment (34/40 points) and professionalism (28/30 points). While the resolution quality was adequate (19/35 points), there's room for improvement in follow-up procedures and proactive communication. The detection of initial frustration patterns was expected given the customer's opening statement, but the positive language that emerged later shows successful de-escalation. To enhance future interactions, we recommend implementing more detailed follow-up protocols, providing customers with clearer timelines upfront, and ensuring all resolution steps are explicitly communicated. The overall positive trajectory and professional handling make this a good example of effective customer service recovery.",
    overallConfidence: "high",
    criteriaEvaluations: {
      sentiment: {
        points: 34,
        maxPoints: 40,
        selectedResponse: "positive",
        confidence: "high",
        reasoning: "Customer expressed satisfaction with resolution",
        color: "#10b981",
      },
      empathy: {
        points: 23,
        maxPoints: 30,
        selectedResponse: "moderate",
        confidence: "high",
        reasoning: "Agent acknowledged frustration and offered help",
        color: "#3b82f6",
      },
      resolution_quality: {
        points: 19,
        maxPoints: 35,
        selectedResponse: "partial",
        confidence: "medium",
        reasoning: "Issue was addressed but follow-up could be better",
        color: "#f59e0b",
      },
      professionalism: {
        points: 28,
        maxPoints: 30,
        selectedResponse: "excellent",
        confidence: "very_high",
        reasoning: "Maintained professional tone throughout",
        color: "#10b981",
      },
    },
    qualityIndicators: {
      escalation_detected: {
        detected: false,
        confidence: "high",
        impact: 0,
        reasoning: "No escalation patterns found",
        color: "#6b7280",
      },
      frustration_patterns: {
        detected: true,
        confidence: "medium",
        impact: -5,
        reasoning: "Initial customer frustration detected",
        color: "#f97316",
      },
      positive_language: {
        detected: true,
        confidence: "high",
        impact: 8,
        reasoning: "Thank you and appreciation expressed",
        color: "#10b981",
      },
    },
    uncertaintyInfo: {
      excludedCriteria: ["communication_clarity"],
      lowConfidenceCount: 1,
    },
  };

  const getConfidenceBadge = (confidence) => {
    const colors = {
      very_high: "bg-emerald-100 text-emerald-800 border-emerald-200",
      high: "bg-blue-100 text-blue-800 border-blue-200",
      medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
      low: "bg-orange-100 text-orange-800 border-orange-200",
      very_low: "bg-red-100 text-red-800 border-red-200",
    };
    return colors[confidence] || "bg-gray-100 text-gray-800 border-gray-200";
  };

  const getHealthBadge = (level) => {
    const colors = {
      excellent: "bg-green-100 text-green-800 border-green-300",
      good: "bg-blue-100 text-blue-800 border-blue-300",
      concerning: "bg-yellow-100 text-yellow-800 border-yellow-300",
      poor: "bg-orange-100 text-orange-800 border-orange-300",
      critical: "bg-red-100 text-red-800 border-red-300",
    };
    return colors[level] || "bg-gray-100 text-gray-800 border-gray-300";
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg shadow-lg p-6 mb-6 text-white">
          <h1 className="text-3xl font-bold mb-2">
            Conversation Health Analysis
          </h1>
          <p className="text-indigo-100">
            Analyze conversation quality with detailed metrics and visual
            insights
          </p>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel - Input */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Input</h2>
                <Settings className="w-5 h-5 text-gray-400" />
              </div>

              {/* Tab Selection */}
              <div className="flex mb-4 border-b">
                <button
                  onClick={() => setActiveTab("test")}
                  className={`px-4 py-2 font-medium text-sm ${
                    activeTab === "test"
                      ? "border-b-2 border-indigo-500 text-indigo-600"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  Test Cases
                </button>
                <button
                  onClick={() => setActiveTab("custom")}
                  className={`px-4 py-2 font-medium text-sm ${
                    activeTab === "custom"
                      ? "border-b-2 border-indigo-500 text-indigo-600"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  Custom Input
                </button>
              </div>

              {activeTab === "test" && (
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-gray-700">
                    Select Test Case
                  </label>
                  <select
                    value={selectedTest}
                    onChange={(e) => setSelectedTest(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="custom">Custom Input</option>
                    <option value="positive_resolution">
                      ✅ Positive Resolution
                    </option>
                    <option value="escalated_complaint">
                      🔥 Escalated Complaint
                    </option>
                    <option value="technical_support">
                      🔧 Technical Support
                    </option>
                    <option value="billing_inquiry">💳 Billing Inquiry</option>
                    <option value="frustrated_customer">
                      😤 Frustrated Customer
                    </option>
                  </select>
                </div>
              )}

              {/* Text Input Area */}
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Conversation Transcript
                </label>
                <textarea
                  placeholder="Enter conversation transcript here or select a test case..."
                  className="w-full h-64 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none text-sm"
                  defaultValue={
                    activeTab === "test"
                      ? "Customer: I'm really frustrated with this billing issue!\nAgent: I understand your frustration. Let me help you resolve this right away.\nCustomer: I've been charged twice for the same service.\nAgent: I can see the duplicate charge here. I'll process a refund immediately and ensure this doesn't happen again.\nCustomer: Thank you so much! That's exactly what I needed.\nAgent: You're welcome! The refund will appear in 3-5 business days."
                      : ""
                  }
                />
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 mt-4">
                <button
                  onClick={() => setShowResults(true)}
                  className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2 font-medium"
                >
                  <Play className="w-4 h-4" />
                  Analyze
                </button>
                <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                  <Save className="w-4 h-4" />
                </button>
                <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                  <Upload className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Right Panel - Results */}
          <div className="lg:col-span-2">
            {showResults ? (
              <div className="space-y-6">
                {/* Overall Score Card */}
                <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-indigo-500">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        Overall Health Score
                      </h3>
                      <p className="text-sm text-gray-600">
                        Comprehensive conversation analysis
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-4xl font-bold text-indigo-600">
                        {mockResults.finalScore}/100
                      </div>
                      <span
                        className={`inline-flex px-3 py-1 rounded-full text-sm font-medium border ${getHealthBadge(
                          mockResults.healthLevel
                        )}`}
                      >
                        {mockResults.healthLevel.toUpperCase()}
                      </span>
                    </div>
                  </div>

                  {/* Score Breakdown Bar */}
                  <div className="mt-6">
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>Critical (0-24)</span>
                      <span>Poor (25-49)</span>
                      <span>Concerning (50-69)</span>
                      <span>Good (70-84)</span>
                      <span>Excellent (85-100)</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-4">
                      <div
                        className="h-4 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500"
                        style={{ width: `${mockResults.finalScore}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                {/* Overall Assessment */}
                <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-purple-500">
                  <div className="flex items-start gap-3 mb-4">
                    <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                      <MessageSquare className="w-4 h-4 text-purple-600" />
                    </div>
                    <div className="flex-grow">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        Overall Assessment
                      </h3>
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-sm text-gray-600">
                          Analysis Confidence:
                        </span>
                        <span
                          className={`px-2 py-1 rounded text-xs border ${getConfidenceBadge(
                            mockResults.overallConfidence
                          )}`}
                        >
                          {mockResults.overallConfidence
                            .replace("_", " ")
                            .toUpperCase()}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-purple-300">
                    <p className="text-gray-700 leading-relaxed text-sm">
                      {mockResults.overallAssessment}
                    </p>
                  </div>

                  <div className="mt-4 flex items-center gap-2 text-xs text-gray-500">
                    <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                    <span>
                      AI-generated summary based on detailed criteria analysis
                    </span>
                  </div>
                </div>

                {/* Evaluation Criteria */}
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    📊 Evaluation Criteria
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(mockResults.criteriaEvaluations).map(
                      ([key, criteria]) => (
                        <div
                          key={key}
                          className="border border-gray-200 rounded-lg p-4"
                          style={{
                            borderLeftColor: criteria.color,
                            borderLeftWidth: "4px",
                          }}
                        >
                          <div className="flex items-center justify-between mb-3">
                            <h4 className="font-semibold text-gray-900 capitalize">
                              {key.replace("_", " ")}
                            </h4>
                            <span
                              className="text-lg font-bold"
                              style={{ color: criteria.color }}
                            >
                              {criteria.points}/{criteria.maxPoints}
                            </span>
                          </div>

                          <div className="mb-3">
                            <span
                              className="inline-flex px-3 py-1 rounded-full text-sm font-medium border"
                              style={{
                                backgroundColor: criteria.color + "20",
                                color: criteria.color,
                                borderColor: criteria.color + "40",
                              }}
                            >
                              {criteria.selectedResponse.toUpperCase()}
                            </span>
                          </div>

                          <div className="flex items-center justify-between mb-2">
                            <div className="w-full bg-gray-200 rounded-full h-2 mr-3">
                              <div
                                className="h-2 rounded-full"
                                style={{
                                  backgroundColor: criteria.color,
                                  width: `${
                                    (criteria.points / criteria.maxPoints) * 100
                                  }%`,
                                }}
                              ></div>
                            </div>
                            <span
                              className={`px-2 py-1 rounded text-xs border ${getConfidenceBadge(
                                criteria.confidence
                              )}`}
                            >
                              {criteria.confidence.replace("_", " ")}
                            </span>
                          </div>

                          <p className="text-sm text-gray-600 mt-2">
                            {criteria.reasoning}
                          </p>
                        </div>
                      )
                    )}
                  </div>
                </div>

                {/* Quality Indicators */}
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    🎯 Quality Indicators
                  </h3>
                  <div className="space-y-3">
                    {Object.entries(mockResults.qualityIndicators).map(
                      ([key, indicator]) => (
                        <div
                          key={key}
                          className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                          style={{
                            borderLeftColor: indicator.color,
                            borderLeftWidth: "4px",
                          }}
                        >
                          <div className="flex items-center gap-4">
                            <div className="flex-shrink-0">
                              {indicator.detected ? (
                                indicator.impact > 0 ? (
                                  <CheckCircle
                                    className="w-6 h-6"
                                    style={{ color: indicator.color }}
                                  />
                                ) : (
                                  <AlertCircle
                                    className="w-6 h-6"
                                    style={{ color: indicator.color }}
                                  />
                                )
                              ) : (
                                <XCircle className="w-6 h-6 text-gray-400" />
                              )}
                            </div>
                            <div className="flex-grow">
                              <div className="flex items-center gap-3 mb-1">
                                <span className="font-semibold text-gray-900 capitalize">
                                  {key.replace("_", " ")}
                                </span>
                                <span
                                  className={`px-2 py-1 rounded text-xs border ${getConfidenceBadge(
                                    indicator.confidence
                                  )}`}
                                >
                                  {indicator.confidence}
                                </span>
                              </div>
                              <p className="text-sm text-gray-600">
                                {indicator.reasoning}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            {indicator.impact !== 0 && (
                              <span
                                className="flex items-center gap-1 text-sm font-semibold px-2 py-1 rounded"
                                style={{
                                  color:
                                    indicator.impact > 0
                                      ? "#10b981"
                                      : "#ef4444",
                                  backgroundColor:
                                    indicator.impact > 0
                                      ? "#d1fae5"
                                      : "#fee2e2",
                                }}
                              >
                                {indicator.impact > 0 ? (
                                  <TrendingUp className="w-4 h-4" />
                                ) : (
                                  <TrendingDown className="w-4 h-4" />
                                )}
                                {Math.abs(indicator.impact)} pts
                              </span>
                            )}
                            <div
                              className="w-4 h-4 rounded-full"
                              style={{
                                backgroundColor: indicator.detected
                                  ? indicator.color
                                  : "#d1d5db",
                              }}
                            ></div>
                          </div>
                        </div>
                      )
                    )}
                  </div>
                </div>

                {/* Uncertainty Info */}
                {mockResults.uncertaintyInfo && (
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertCircle className="w-5 h-5 text-amber-600" />
                      <h4 className="font-medium text-amber-800">
                        Analysis Notes
                      </h4>
                    </div>
                    <div className="text-sm text-amber-700">
                      {mockResults.uncertaintyInfo.excludedCriteria.length >
                        0 && (
                        <p>
                          • Excluded criteria due to low confidence:{" "}
                          <span className="font-medium">
                            {mockResults.uncertaintyInfo.excludedCriteria.join(
                              ", "
                            )}
                          </span>
                        </p>
                      )}
                      {mockResults.uncertaintyInfo.lowConfidenceCount > 0 && (
                        <p>
                          • {mockResults.uncertaintyInfo.lowConfidenceCount}{" "}
                          evaluation(s) had lower confidence levels
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Ready to Analyze
                </h3>
                <p className="text-gray-600">
                  Enter a conversation transcript and click "Analyze" to see
                  detailed health metrics with points breakdown
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConversationHealthMockup;
