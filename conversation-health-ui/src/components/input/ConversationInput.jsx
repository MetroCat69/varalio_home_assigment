import React from "react";
import Textarea from "../ui/Textarea";
import { TEST_CASES } from "../../utils/constants";

const ConversationInput = ({
  value,
  onChange,
  selectedTest,
  disabled = false,
  placeholder = "Enter conversation transcript here...",
}) => {
  // Get transcript from selected test case
  const getTestCaseTranscript = () => {
    if (selectedTest && selectedTest !== "custom" && TEST_CASES[selectedTest]) {
      return TEST_CASES[selectedTest].transcript;
    }
    return "";
  };

  const displayValue =
    selectedTest !== "custom" ? getTestCaseTranscript() : value;
  const isReadOnly = selectedTest !== "custom";

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        Conversation Transcript
      </label>
      <Textarea
        value={displayValue}
        onChange={isReadOnly ? undefined : onChange}
        placeholder={
          isReadOnly ? "Test case transcript will appear here..." : placeholder
        }
        className="h-64 text-sm"
        disabled={disabled}
        readOnly={isReadOnly}
      />
      {isReadOnly && (
        <p className="text-xs text-gray-500">
          This is a preview of the selected test case. Switch to "Custom Input"
          to enter your own transcript.
        </p>
      )}
    </div>
  );
};

export default ConversationInput;
