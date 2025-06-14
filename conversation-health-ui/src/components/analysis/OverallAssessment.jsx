import React from "react";
import { MessageSquare } from "lucide-react";
import { Card, CardContent } from "../ui/Card";
import Badge from "../ui/Badge";
import { getConfidenceBadge, formatConfidence } from "../../utils/helpers";

const OverallAssessment = ({ results }) => {
  const { overallAssessment, overallConfidence } = results;

  return (
    <Card className="border-l-4 border-purple-500">
      <CardContent className="p-6">
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
              <Badge className={getConfidenceBadge(overallConfidence)}>
                {formatConfidence(overallConfidence)}
              </Badge>
            </div>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-purple-300">
          <p className="text-gray-700 leading-relaxed text-sm">
            {overallAssessment}
          </p>
        </div>

        <div className="mt-4 flex items-center gap-2 text-xs text-gray-500">
          <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
          <span>AI-generated summary based on detailed criteria analysis</span>
        </div>
      </CardContent>
    </Card>
  );
};

export default OverallAssessment;
