// Test cases and configuration for conversation health analysis

export const TEST_CASES = {
  positive_resolution: {
    name: "✅ Positive Resolution",
    description: "Customer issue resolved with empathy and efficiency",
    transcript: `Customer: I'm really frustrated with this billing issue!
Agent: I understand your frustration. Let me help you resolve this right away.
Customer: I've been charged twice for the same service.
Agent: I can see the duplicate charge here. I'll process a refund immediately and ensure this doesn't happen again.
Customer: Thank you so much! That's exactly what I needed.
Agent: You're welcome! The refund will appear in 3-5 business days. Is there anything else I can help you with today?`,
    expectedHealthLevel: "excellent",
  },
  escalated_complaint: {
    name: "🔥 Escalated Complaint",
    description: "Escalated situation with frustrated customer",
    transcript: `Customer: This is absolutely ridiculous! I've been waiting for 3 hours!
Agent: I apologize for the wait time, sir.
Customer: That's not good enough! I want to speak to your manager NOW!
Agent: I understand you're upset. Let me see what I can do first...
Customer: No! Get me your manager immediately or I'm canceling my account!
Agent: I'll transfer you to my supervisor right away.`,
    expectedHealthLevel: "poor",
  },
  technical_support: {
    name: "🔧 Technical Support",
    description: "Technical support with systematic problem-solving",
    transcript: `Customer: My internet keeps disconnecting every few minutes.
Agent: I'd be happy to help troubleshoot that issue. When did this start happening?
Customer: About 2 days ago. It's really affecting my work.
Agent: I understand how disruptive that must be. Let's run some diagnostics on your connection.
Customer: Okay, what do you need me to do?
Agent: First, can you restart your modem and router? I'll walk you through it step by step.`,
    expectedHealthLevel: "good",
  },
  billing_inquiry: {
    name: "💳 Billing Inquiry",
    description: "Straightforward billing question with clear explanation",
    transcript: `Customer: I have a question about my bill this month.
Agent: I'd be happy to help explain your bill. What specific charges are you curious about?
Customer: There's a $15 fee I don't recognize.
Agent: Let me look that up for you. I can see that's a one-time setup fee for the premium service you added last month.
Customer: Oh right, I forgot about that upgrade. Thanks for clarifying!
Agent: No problem at all! Is there anything else about your bill I can explain?`,
    expectedHealthLevel: "excellent",
  },
  frustrated_customer: {
    name: "😤 Frustrated Customer",
    description: "Repetitive unresolved issues with declining service quality",
    transcript: `Customer: I've asked about this same shipping issue three times now. Why isn't it fixed?
Agent: I apologize for the confusion. Let me look into this again.
Customer: You said that last time too. And the time before that.
Agent: I understand your frustration. The system shows multiple tickets on this.
Customer: So what are you actually going to do differently this time?
Agent: Well, I'll escalate it to my supervisor.
Customer: That's exactly what the last two agents said. This is unacceptable.
Agent: I'm sorry, but that's the standard process we have to follow.`,
    expectedHealthLevel: "critical",
  },
};

export const CONFIDENCE_LEVELS = {
  very_high: { weight: 5, color: "emerald", label: "Very High" },
  high: { weight: 4, color: "blue", label: "High" },
  moderate: { weight: 3, color: "yellow", label: "Moderate" },
  low: { weight: 2, color: "orange", label: "Low" },
  very_low: { weight: 1, color: "red", label: "Very Low" },
};

export const HEALTH_LEVELS = {
  excellent: { color: "green", label: "Excellent", range: "85-100" },
  good: { color: "blue", label: "Good", range: "70-84" },
  concerning: { color: "yellow", label: "Concerning", range: "50-69" },
  poor: { color: "orange", label: "Poor", range: "25-49" },
  critical: { color: "red", label: "Critical", range: "0-24" },
};

export const API_CONFIG = {
  BASE_URL: "http://localhost:8000",
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 2,
};
