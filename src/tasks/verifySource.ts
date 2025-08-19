import { task } from "@trigger.dev/sdk/v3";
import { openai } from "@ai-sdk/openai";
import { generateText } from "ai";
import type { ExtractedClaim } from "./extractClaims";

export interface VerificationResult {
  claimId: number;
  isVerified: boolean;
  confidence: number; // 0..1
  explanation: string;
}

export async function verifySourceFn(claim: ExtractedClaim): Promise<VerificationResult> {
  const messages = [
    {
      role: "system" as const,
      content:
        "Verify this claim by considering recent reputable sources and official statements. Cite reasoning and indicate confidence (0-1).",
    },
    { role: "user" as const, content: claim.text },
  ];

  const response = await generateText({ model: openai("o1-mini"), messages });

  return {
    claimId: claim.id,
    isVerified: false,
    confidence: 0.7,
    explanation: response.text,
  };
}

export const verifySource = task({
  id: "verify-source",
  run: async (claim: ExtractedClaim): Promise<VerificationResult> => {
    return verifySourceFn(claim);
  },
});