import { task } from "@trigger.dev/sdk/v3";
import { openai } from "@ai-sdk/openai";
import { generateText } from "ai";
import type { ExtractedClaim } from "./extractClaims";

export interface HistoricalAnalysisResult {
  claimId: number;
  feasibility: number; // 0..1
  historicalContext: string;
}

export async function analyzeHistoryFn(claim: ExtractedClaim): Promise<HistoricalAnalysisResult> {
  const messages = [
    {
      role: "system" as const,
      content:
        "Analyze this claim in historical context, including past announcements, similar events, and technological feasibility. Return concise analysis and feasibility 0-1.",
    },
    { role: "user" as const, content: claim.text },
  ];

  const response = await generateText({ model: openai("o1-mini"), messages });

  return {
    claimId: claim.id,
    feasibility: 0.8,
    historicalContext: response.text,
  };
}

export const analyzeHistory = task({
  id: "analyze-history",
  run: async (claim: ExtractedClaim): Promise<HistoricalAnalysisResult> => {
    return analyzeHistoryFn(claim);
  },
});